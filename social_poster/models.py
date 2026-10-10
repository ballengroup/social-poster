from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class Video:
    """One piece of content moving through the pipeline."""

    source: str  # e.g. "tiktok" or "local"
    source_id: str  # stable id on the source platform, used for de-duping
    caption: str = ""
    url: str = ""
    path: Path | None = None  # local mp4 once downloaded
    asins: list[str] = field(default_factory=list)


@dataclass
class PostResult:
    ok: bool
    detail: str = ""
