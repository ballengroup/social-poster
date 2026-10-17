"""Loads config.yaml, with environment variables taking precedence."""

import os
from dataclasses import dataclass, field
from pathlib import Path

import yaml


@dataclass
class Config:
    tiktok_handle: str
    tiktok_sec_uid: str = ""
    check_latest: int = 15
    output_dir: Path = Path("kits")
    state_file: Path = Path("state.json")
    gdrive_folder_id: str = ""
    drop_hashtags: list[str] = field(default_factory=list)
    add_hashtags: list[str] = field(default_factory=list)


def load_config(path: str | Path = "config.yaml") -> Config:
    data = {}
    path = Path(path)
    if path.exists():
        data = yaml.safe_load(path.read_text()) or {}

    handle = os.environ.get("TIKTOK_HANDLE") or data.get("tiktok_handle") or ""
    handle = handle.strip().lstrip("@")
    if not handle or handle == "your_handle":
        raise SystemExit("Set tiktok_handle in config.yaml or the TIKTOK_HANDLE env var.")

    return Config(
        tiktok_handle=handle,
        tiktok_sec_uid=os.environ.get("TIKTOK_SEC_UID") or data.get("tiktok_sec_uid") or "",
        check_latest=int(data.get("check_latest", 15)),
        output_dir=Path(os.environ.get("OUTPUT_DIR") or data.get("output_dir", "kits")),
        state_file=Path(data.get("state_file", "state.json")),
        gdrive_folder_id=os.environ.get("GDRIVE_FOLDER_ID") or data.get("gdrive_folder_id") or "",
        drop_hashtags=[h.lower().lstrip("#") for h in data.get("drop_hashtags") or []],
        add_hashtags=[h.lstrip("#") for h in data.get("add_hashtags") or []],
    )
