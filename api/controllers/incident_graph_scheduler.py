import threading
from typing import List

from controllers.incident_service import IncidentService
from controllers.event_graph_service import EventGraphService, EventGraphGenerationError
from models.incident import Incident
from utils.app_config import config
from utils.common_utils import scheduler
from utils.logger_init import logger


class IncidentGraphIntelligenceJob:
    """Periodic job that keeps incident graph data in sync when alert_list changes."""

    JOB_ID = "incident_graph_alert_sync"
    _lock = threading.Lock()

    @classmethod
    def register(cls):
        interval = config.get("application.incident_graph.refresh_interval_seconds")
        if not interval:
            logger.warning("[IncidentGraphJob] refresh interval missing, scheduler stopped.")
            return

        scheduler.add_job(
            id=cls.JOB_ID,
            func=cls.run,
            trigger="interval",
            seconds=int(interval),
            max_instances=1,
            coalesce=True,
            misfire_grace_time=int(interval),
            replace_existing=True,
        )
        logger.info("[IncidentGraphJob] Registered incident graph sync job (every %ss)", interval)

    @classmethod
    def run(cls):
        with cls._lock:
            snapshots = Incident.list_incident_alert_snapshots(only_open=True)
            light_rag_enabled = EventGraphService.is_configured()
            logger.debug("[IncidentGraphJob] Scanning %s open incidents for alert changes", len(snapshots))
            for snapshot in snapshots:
                incident_id = snapshot.get("incident_id")
                if not incident_id:
                    continue
                try:
                    remote_payload = IncidentService.retrieve_incident_by_id(
                        incident_id,
                        include_graph=False,
                        sync_local=False,
                    )
                except Exception as exc:
                    logger.warning("[IncidentGraphJob] Failed to fetch incident %s: %s", incident_id, exc)
                    continue

                stored_alerts = cls._normalize_alert_list(snapshot.get("alert_list"))
                remote_alerts = cls._normalize_alert_list(remote_payload.get("alert_list"))

                alerts_changed = not cls._alert_counts_equal(stored_alerts, remote_alerts)
                graph_missing = cls._graph_bundle_missing(snapshot)

                if not alerts_changed and not graph_missing:
                    continue

                if alerts_changed:
                    logger.info(
                        "[IncidentGraphJob] Detected alert count change for %s: local=%s remote=%s",
                        incident_id,
                        len(stored_alerts),
                        len(remote_alerts),
                    )
                    try:
                        Incident.upsert_incident(remote_payload)
                    except Exception as exc:
                        logger.warning("[IncidentGraphJob] Failed to update local snapshot for %s: %s", incident_id, exc)
                        continue
                else:
                    logger.info(
                        "[IncidentGraphJob] Missing graph bundle for %s (graph_data=%s, graph_summary=%s)",
                        incident_id,
                        "present" if snapshot.get("has_graph_data") else "missing",
                        "present" if snapshot.get("has_graph_summary") else "missing",
                    )

                associated_alerts = remote_payload.get("associated_alerts", [])
                if light_rag_enabled:
                    cls._refresh_graph_bundle(incident_id, remote_payload, associated_alerts)
                else:
                    logger.debug("[IncidentGraphJob] LightRAG disabled, skip graph refresh for %s", incident_id)

    @staticmethod
    def _normalize_alert_list(values):
        if not values:
            return []
        if isinstance(values, list):
            return [str(item) for item in values if item is not None]
        return []

    @staticmethod
    def _alert_counts_equal(left: List[str], right: List[str]) -> bool:
        return len(left) == len(right)

    @staticmethod
    def _graph_bundle_missing(snapshot: dict) -> bool:
        return (not snapshot.get("has_graph_data", False)) or (not snapshot.get("has_graph_summary", False))

    @staticmethod
    def _refresh_graph_bundle(incident_id: str, incident_payload: dict, associated_alerts: List[dict]):
        try:
            graph_data, graph_summary = EventGraphService.generate_graph_bundle(incident_payload, associated_alerts)
            Incident.update_graph_bundle(incident_id, graph_data=graph_data, graph_summary=graph_summary)
            logger.info("[IncidentGraphJob] Refreshed graph bundle for %s", incident_id)
        except EventGraphGenerationError as exc:
            logger.warning("[IncidentGraphJob] LightRAG update failed for %s: %s", incident_id, exc)
        except Exception:
            logger.exception("[IncidentGraphJob] Unexpected error while refreshing graph for %s", incident_id)

