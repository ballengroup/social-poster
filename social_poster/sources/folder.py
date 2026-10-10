"""Use a plain folder as the source: your original, watermark-free video files."""

import hashlib
from pathlib import Path

from ..models import Video

VIDEO_EXTS = {".mp4", ".mov", ".m4v"}


class FolderSource:
    name = "local"

    def __init__(self, inbox: Path):
        self.inbox = inbox

    def scan(self) -> list[Video]:
        self.inbox.mkdir(parents=True, exist_ok=True)
        videos = []
        for path in sorted(self.inbox.iterdir()):
            if path.suffix.lower() not in VIDEO_EXTS or path.name.startswith("."):
                continue
            caption_file = path.with_suffix(".txt")
            caption = caption_file.read_text().strip() if caption_file.exists() else ""
            videos.append(Video(self.name, _fingerprint(path), caption=caption, path=path))
        return videos


def _fingerprint(path: Path) -> str:
    """Hash of the file contents, so renaming a file doesn't make it 'new' again."""
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()[:16]
