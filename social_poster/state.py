"""Remembers which TikTok videos already have a kit, so each run only picks up new ones."""

import json
from datetime import datetime, timezone
from pathlib import Path


class State:
    def __init__(self, path: Path):
        self.path = path
        self.done: dict[str, dict] = {}
        if path.exists():
            self.done = json.loads(path.read_text()).get("done", {})

    def is_done(self, video_id: str) -> bool:
        return video_id in self.done

    def mark_done(self, video_id: str, title: str, kit_dir: str) -> None:
        self.done[video_id] = {
            "title": title,
            "kit": kit_dir,
            "processed_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        }
        self.save()

    def save(self) -> None:
        self.path.write_text(json.dumps({"done": self.done}, indent=2, ensure_ascii=False) + "\n")
