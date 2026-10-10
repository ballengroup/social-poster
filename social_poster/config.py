"""Load config.yaml and fill in defaults."""

import copy
import os
from pathlib import Path

import yaml

DEFAULTS = {
    "data_dir": "data",
    # Drop original video files here (with an optional same-name .txt caption).
    "inbox_dir": "inbox",
    "amazon": {
        "enabled": True,
        "upload_url": "https://www.amazon.com/creatorhub/video/upload",
        "only_hashtag": "",  # e.g. "amazonfinds" -> only make kits for captions with that tag
        "require_product_link": False,  # skip videos with no Amazon link in the caption
    },
    "tiktok_publish": {
        "enabled": False,
        # Content Posting API user token with the video.upload scope.
        # Leave blank and set TIKTOK_ACCESS_TOKEN in your environment instead.
        "access_token": "",
    },
    "watch": {"interval_minutes": 5},
}


def _merge(base: dict, override: dict) -> dict:
    out = copy.deepcopy(base)
    for key, value in (override or {}).items():
        if isinstance(value, dict) and isinstance(out.get(key), dict):
            out[key] = _merge(out[key], value)
        else:
            out[key] = value
    return out


def load(path: str | Path = "config.yaml") -> dict:
    path = Path(path)
    user = yaml.safe_load(path.read_text()) if path.exists() else {}
    cfg = _merge(DEFAULTS, user or {})
    cfg["data_dir"] = Path(cfg["data_dir"]).expanduser()
    cfg["inbox_dir"] = Path(cfg["inbox_dir"]).expanduser()
    if not cfg["tiktok_publish"]["access_token"]:
        cfg["tiktok_publish"]["access_token"] = os.environ.get("TIKTOK_ACCESS_TOKEN", "")
    return cfg
