import json
import random
from typing import Dict, List

from flask import request
from flask_restful import Resource

from utils.auth_util import auth_required
from utils.logger_init import logger


PROMPT_CONFIG_PATH = "resources/ai_prompts.json"
SUPPORTED_LANGS = {"zh", "en"}
PROMPT_CONFIG: Dict = {}


def _load_config() -> Dict:
    global PROMPT_CONFIG
    if PROMPT_CONFIG:
        return PROMPT_CONFIG
    try:
        with open(PROMPT_CONFIG_PATH, "r", encoding="utf-8") as f:
            PROMPT_CONFIG = json.load(f) or {}
    except FileNotFoundError:
        logger.warning("[AI Prompt] Config file %s not found", PROMPT_CONFIG_PATH)
        PROMPT_CONFIG = {}
    except Exception as exc:  # pylint: disable=broad-except
        logger.exception("[AI Prompt] Failed to load config: %s", exc)
        PROMPT_CONFIG = {}
    return PROMPT_CONFIG


def _norm_route(raw: str) -> str:
    if not raw:
        return ""
    path = raw.split("?")[0].strip()
    if not path.startswith("/"):
        path = "/" + path
    return path.rstrip("/") or "/"


def _norm_lang(raw: str) -> str:
    raw = (raw or "").lower()
    if raw.startswith("zh"):
        return "zh"
    if raw.startswith("en"):
        return "en"
    return raw


class AIPromptView(Resource):
    @auth_required
    def get(self, username=None):
        route = _norm_route(request.args.get("route", ""))
        lang = _norm_lang(request.args.get("lang", ""))

        if not route:
            return {"error_message": "route is required"}, 400
        if lang not in SUPPORTED_LANGS:
            return {"error_message": "lang must be zh or en"}, 400

        route_key = route
        if route.startswith("/alerts/") and route.count("/") == 2:
            route_key = "/alerts/detail"

        config = _load_config()
        entries = config.get(route_key) or []

        prompts = [item.get(lang) for item in entries if isinstance(item, dict) and item.get(lang)]

        take = min(3, len(prompts))
        chosen = random.sample(prompts, k=take) if len(prompts) > take else prompts

        return {"data": chosen}, 200

