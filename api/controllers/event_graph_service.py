import json
import time
from threading import Lock
from typing import List, Tuple, Optional, Dict, Any

import requests

from utils.app_config import config
from utils.logger_init import logger
from utils.common_utils import get_proxy

DEFAULT_SUMMARY_PROMPT = """
You are a cybersecurity analyst. Based on the following incident information retrieved from the SIEM system and knowledge base, generate a concise and structured security incident summary. The summary should include:
1. Overview: incident ID/name, occurrence time, attack type (e.g., ransomware, APT, DDoS, intrusion)
2. Attack progression: attack trigger, propagation path, key alerts, and incident chain
3. Impact: affected assets (servers, applications, network devices), business systems, users, alert severity and count
4. Related alerts: highlight key or high-severity alerts associated with this incident
5. Possible causes or context: exploited vulnerabilities, attack techniques, attacker behavior patterns (if available)
6. Recommendations or preliminary mitigation steps (if available)

Requirements:
- Present the summary in readable paragraphs, not just a list of alerts or logs
- Include comprehensive but concise information, focusing on key points, around 200–300 words
- Keep only critical alert information, ignore duplicates or low-priority alerts
""".strip()

class EventGraphGenerationError(Exception):
    """Custom exception for LightRAG graph generation failures."""


class _LightRAGClient:
    """Lightweight client wrapper around the LightRAG REST API."""

    def __init__(self):
        self.base_url = config.get("application.lightrag.base_url")
        if not self.base_url:
            raise EventGraphGenerationError("LightRAG base_url is not configured")

        self.timeout = config.get("application.lightrag.request_timeout_seconds", 30)
        self.poll_interval = config.get("application.lightrag.poll_interval_seconds", 3)
        self.workspace_timeout = config.get("application.lightrag.workspace_timeout_seconds", 180)
        self.track_timeout = config.get("application.lightrag.track_timeout_seconds", 420)
        self.api_key = config.get("application.lightrag.api_key")

    def ensure_workspace_empty(self):
        """Block until the LightRAG workspace reports zero documents."""
        start = time.monotonic()
        while True:
            counts = self._get_status_counts()
            if sum(counts.values()) == 0:
                return

            if time.monotonic() - start > self.workspace_timeout:
                raise EventGraphGenerationError(
                    f"LightRAG workspace busy for more than {self.workspace_timeout} seconds"
                )
            time.sleep(self.poll_interval)

    def insert_text(self, payload_text: str, file_source: Optional[str] = None) -> str:
        response = self._request(
            "POST",
            "/documents/text",
            json={"text": payload_text, **({"file_source": file_source} if file_source else {})},
        )
        data = self._safe_json(response)
        track_id = data.get("track_id") or data.get("data", {}).get("track_id")
        if not track_id:
            raise EventGraphGenerationError("LightRAG insert_text response missing track_id")
        return track_id

    def wait_for_track_completion(self, track_id: str):
        """Poll track status until all documents are processed."""
        start = time.monotonic()
        completed_states = {"PROCESSED", "PREPROCESSED"}
        failure_states = {"FAILED", "ERROR"}

        latest_documents = []

        while True:
            response = self._request("GET", f"/documents/track_status/{track_id}")
            data = self._safe_json(response)
            documents = data.get("documents") or data.get("data", {}).get("documents") or []
            if documents:
                latest_documents = documents

                statuses = {doc.get("status", "").upper() for doc in documents if doc.get("status")}
                if statuses and statuses.issubset(completed_states):
                    return latest_documents
                if statuses & failure_states:
                    raise EventGraphGenerationError(
                        f"LightRAG document processing failed for track {track_id}: {statuses}"
                    )

            if time.monotonic() - start > self.track_timeout:
                raise EventGraphGenerationError(
                    f"Timed out waiting for LightRAG track {track_id} to complete"
                )
            time.sleep(self.poll_interval)

    def fetch_graph_data(self, doc_id: Optional[str], label_candidates: List[str]) -> Dict[str, Any]:
        label_priority = self._resolve_graph_labels(doc_id)
        label_priority.extend(label_candidates)

        last_error = None
        tried = []
        for label in label_priority:
            if not label:
                continue
            try:
                logger.info("[LightRAG] Fetching graph with label='%s' doc_id='%s'", label, doc_id)
                return self._fetch_graph_by_label(label, doc_id)
            except EventGraphGenerationError as exc:
                tried.append(label)
                last_error = exc
                logger.warning("[LightRAG] Graph fetch failed for label '%s': %s", label, exc)

        if last_error:
            raise EventGraphGenerationError(
                f"Unable to fetch graph with labels {tried}: {last_error}"
            ) from last_error
        raise EventGraphGenerationError("No valid label provided to fetch graph data")

    def _resolve_graph_labels(self, doc_id: Optional[str]) -> List[str]:
        labels = ["*"]
        if doc_id:
            try:
                response = self._request("GET", "/graph/label/list", params={"doc_id": doc_id})
                data = self._safe_json(response)
                if isinstance(data, dict):
                    labels.extend(data.get("labels") or [])
                elif isinstance(data, list):
                    labels.extend(data)
            except EventGraphGenerationError as exc:
                logger.warning("[LightRAG] Failed to list labels for doc_id=%s: %s", doc_id, exc)
        return [label for label in labels if label]

    def _fetch_graph_by_label(self, label: str, doc_id: Optional[str]) -> Dict[str, Any]:
        params = {
            "label": label,
            "max_depth": config.get("application.lightrag.graph_max_depth", 3),
            "max_nodes": config.get("application.lightrag.graph_max_nodes", 500),
        }
        if doc_id:
            params["doc_id"] = doc_id
        response = self._request("GET", "/graphs", params=params)
        data = self._safe_json(response)
        if "graph" in data and isinstance(data["graph"], dict):
            return data["graph"]
        return data

    def query_summary(self, summary_prompt: str) -> Optional[str]:
        body = {
            "query": summary_prompt,
            "mode": "mix",
            "include_references": False,
            "response_type": "Multiple Paragraphs",
            "top_k": 40,
            "chunk_top_k": 20,
            "max_entity_tokens": 6000,
            "max_relation_tokens": 8000,
            "enable_rerank": True,
            "max_total_tokens": 30000,
        }
        response = self._request("POST", "/query", json=body)
        data = self._safe_json(response)
        return data.get("response") or data.get("data")

    def clear_documents(self):
        try:
            self._request("DELETE", "/documents")
        except EventGraphGenerationError as exc:
            logger.warning("Failed to clear LightRAG workspace: %s", exc)

    def _get_status_counts(self) -> Dict[str, int]:
        response = self._request("GET", "/documents/status_counts")
        data = self._safe_json(response)
        raw_counts = data.get("status_counts") or data.get("data") or data
        counts = {}
        if isinstance(raw_counts, dict):
            for key, value in raw_counts.items():
                try:
                    counts[key] = int(value)
                except (TypeError, ValueError):
                    counts[key] = 0
        return counts

    def _request(self, method: str, path: str, *, params=None, json=None):
        url = f"{self.base_url.rstrip('/')}{path}"
        params = params.copy() if params else {}
        if self.api_key:
            params.setdefault("api_key_header_value", self.api_key)

        # Get proxies from config and set verify=False
        proxies = get_proxy("proxyde.huawei.com", "8080") 

        try:
            response = requests.request(
                method=method,
                url=url,
                params=params,
                json=json,
                timeout=self.timeout,
                verify=False,
                proxies=proxies
            )
        except requests.RequestException as exc:
            raise EventGraphGenerationError(f"LightRAG request error: {exc}") from exc

        if response.status_code >= 400:
            raise EventGraphGenerationError(
                f"LightRAG API {method} {path} failed with status {response.status_code}: {response.text}"
            )
        self._log_response(method, path, response)
        return response

    @staticmethod
    def _safe_json(response: requests.Response) -> dict:
        try:
            return response.json()
        except ValueError as exc:
            raise EventGraphGenerationError("LightRAG API returned invalid JSON") from exc

    @staticmethod
    def _log_response(method: str, path: str, response: requests.Response):
        body = response.text or ""
        truncated = (body[:800] + "...") if len(body) > 800 else body
        safe_body = truncated or "<empty-body>"
        if hasattr(safe_body, "isascii") and not safe_body.isascii():
            try:
                safe_body = safe_body.encode("ascii", errors="replace").decode("ascii")
            except Exception:
                safe_body = "<non-ascii-body>"

        noisy_paths = ("/documents/track_status", "/documents/status_counts")
        log_fn = logger.debug if any(path.startswith(noisy) for noisy in noisy_paths) else logger.info
        log_fn("[LightRAG] %s %s -> %s %s", method, path, response.status_code, safe_body)


class EventGraphService:
    """Facade that orchestrates LightRAG workflow for incident graphs."""

    _lock = Lock()
    _max_alerts = 10

    @classmethod
    def is_configured(cls) -> bool:
        return bool(config.get("application.lightrag.base_url"))

    @classmethod
    def generate_graph_bundle(cls, incident_payload: dict, associated_alerts: List[dict]) -> Tuple[Dict[str, Any], Optional[str]]:
        if not cls.is_configured():
            raise EventGraphGenerationError("LightRAG service is not configured")

        with cls._lock:
            client = _LightRAGClient()
            payload_text = cls._build_insert_payload(incident_payload, associated_alerts)
            label_candidates = cls._build_graph_label_candidates(incident_payload, associated_alerts)
            file_source = cls._build_file_source(incident_payload)
            summary_prompt = cls._build_summary_prompt(incident_payload)
            max_attempts = max(1, config.get("application.lightrag.max_retry_attempts", 1))

            for attempt in range(1, max_attempts + 1):
                has_documents = False
                try:
                    client.ensure_workspace_empty()
                    track_id = client.insert_text(payload_text, file_source=file_source)
                    has_documents = True
                    documents = client.wait_for_track_completion(track_id)
                    doc_id = documents[0].get("id") if documents else None
                    graph_data = client.fetch_graph_data(doc_id, label_candidates)
                    graph_summary = client.query_summary(summary_prompt)
                    logger.info(
                        "[EventGraph] Generated graph for incident %s (nodes=%s, edges=%s)",
                        incident_payload.get("id"),
                        len(graph_data.get("nodes", [])) if isinstance(graph_data, dict) else "unknown",
                        len(graph_data.get("edges", [])) if isinstance(graph_data, dict) else "unknown",
                    )
                    client.clear_documents()
                    return graph_data, graph_summary
                except EventGraphGenerationError as exc:
                    logger.warning(
                        "[EventGraph] Attempt %s/%s failed for incident %s: %s",
                        attempt,
                        max_attempts,
                        incident_payload.get("id"),
                        exc,
                    )
                    if has_documents:
                        try:
                            client.clear_documents()
                        except EventGraphGenerationError as cleanup_exc:
                            logger.warning("[EventGraph] Failed to clear LightRAG workspace: %s", cleanup_exc)
                    if attempt >= max_attempts:
                        raise
                    time.sleep(client.poll_interval)

    @classmethod
    def _build_insert_payload(cls, incident_payload: dict, associated_alerts: List[dict]) -> str:
        """Combine incident and alert context into a single string payload for LightRAG."""
        parts: List[str] = []

        title = incident_payload.get("title") or incident_payload.get("name") or ""
        description = cls._stringify_value(incident_payload.get("description"))
        severity = incident_payload.get("severity") or "-"
        labels = incident_payload.get("labels")
        labels_text = ", ".join(labels) if isinstance(labels, list) else labels or "-"
        handle_status = incident_payload.get("handle_status") or incident_payload.get("status") or "-"

        parts.append(f"Incident ID: {incident_payload.get('id')}")
        parts.append(f"Incident Title: {title}")
        parts.append(f"Incident Severity: {severity}")
        parts.append(f"Incident Status: {handle_status}")
        parts.append(f"Incident Labels: {labels_text}")
        parts.append(f"Incident Description: {description}")

        if incident_payload.get("owner"):
            parts.append(f"Owner: {incident_payload.get('owner')}")
        if incident_payload.get("responsible_person"):
            parts.append(f"Responsible Person: {incident_payload.get('responsible_person')}")
        if incident_payload.get("responsible_dept"):
            parts.append(f"Responsible Department: {incident_payload.get('responsible_dept')}")

        if associated_alerts:
            parts.append("Associated Alerts:")
            for idx, alert in enumerate(associated_alerts[: cls._max_alerts], start=1):
                alert_desc = cls._stringify_value(alert.get("description"))
                parts.append(f"  Alert {idx} Title: {alert.get('title', '-')}")
                parts.append(f"  Alert Severity: {alert.get('severity', '-')}, Status: {alert.get('handle_status', '-')}")
                if alert_desc:
                    parts.append(f"  Alert Description: {alert_desc}")
                if alert.get("data_source_product_name"):
                    parts.append(f"  Data Source: {alert.get('data_source_product_name')}")
                parts.append("")

        return "\n".join(parts).strip()

    @staticmethod
    def _build_file_source(incident_payload: dict) -> str:
        incident_id = incident_payload.get("id") or incident_payload.get("incident_id") or "unknown"
        return f"incident::{incident_id}"

    @staticmethod
    def _build_graph_label_candidates(incident_payload: dict, associated_alerts: List[dict]) -> List[str]:
        candidates = []

        def add(value):
            if value:
                value = str(value).strip()
                if value:
                    candidates.append(value)

        add(incident_payload.get("title"))
        add(incident_payload.get("name"))
        add(incident_payload.get("id"))
        add(incident_payload.get("incident_id"))

        for alert in associated_alerts or []:
            add(alert.get("title"))
            add(alert.get("id"))

        candidates.extend(["incident", "event", "alert"])

        deduped = []
        seen = set()
        for value in candidates:
            if value not in seen:
                deduped.append(value)
                seen.add(value)
        return deduped

    @staticmethod
    def _build_summary_prompt(incident_payload: dict) -> str:
        del incident_payload  # title currently unused but keep signature for future context
        configured_prompt = config.get("application.lightrag.prompt")
        prompt = configured_prompt or DEFAULT_SUMMARY_PROMPT
        return str(prompt).strip()

    @staticmethod
    def _stringify_value(value: Any) -> str:
        if value is None:
            return ""
        if isinstance(value, str):
            return value
        try:
            return json.dumps(value, ensure_ascii=False)
        except (TypeError, ValueError):
            return str(value)


