"""Lists and downloads videos from a TikTok profile using yt-dlp."""

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

import yt_dlp


@dataclass
class Video:
    id: str
    url: str
    description: str
    uploaded: datetime | None


def _base_opts() -> dict:
    return {"quiet": True, "no_warnings": True}


def list_recent(handle: str, limit: int, sec_uid: str = "") -> list[Video]:
    """Newest-first list of the profile's latest videos (metadata only, nothing downloaded).

    sec_uid skips the profile-page lookup, which TikTok sometimes blocks.
    """
    opts = _base_opts() | {"extract_flat": "in_playlist", "playlistend": limit}
    source = f"tiktokuser:{sec_uid}" if sec_uid else f"https://www.tiktok.com/@{handle}"
    with yt_dlp.YoutubeDL(opts) as ydl:
        info = ydl.extract_info(source, download=False)

    videos = []
    for entry in info.get("entries") or []:
        if not entry or not entry.get("id"):
            continue
        ts = entry.get("timestamp")
        videos.append(
            Video(
                id=str(entry["id"]),
                url=entry.get("url") or f"https://www.tiktok.com/@{handle}/video/{entry['id']}",
                description=entry.get("description") or entry.get("title") or "",
                uploaded=datetime.fromtimestamp(ts, timezone.utc) if ts else None,
            )
        )
    return videos


def _no_watermark_first(ctx):
    """Format selector: best non-watermarked mp4, falling back to whatever is best."""
    formats = [f for f in ctx["formats"] if f.get("vcodec") != "none"]
    clean = [f for f in formats if "watermark" not in (f.get("format_note") or "").lower()]
    pool = clean or formats
    best = max(pool, key=lambda f: ((f.get("height") or 0), (f.get("tbr") or 0)))
    yield best


def download(video: Video, dest_dir: Path) -> tuple[Path, Path | None, dict]:
    """Download the video and its cover into dest_dir. Returns (video_path, cover_path, info)."""
    dest_dir.mkdir(parents=True, exist_ok=True)
    opts = _base_opts() | {
        "format": _no_watermark_first,
        "outtmpl": str(dest_dir / "video.%(ext)s"),
        "writethumbnail": True,
    }
    with yt_dlp.YoutubeDL(opts) as ydl:
        info = ydl.extract_info(video.url, download=True)

    files = list(dest_dir.glob("video.*"))
    images = [p for p in files if p.suffix.lower() in IMAGE_SUFFIXES]
    video_path = next(p for p in files if p not in images)
    cover = images[0].rename(dest_dir / f"cover{images[0].suffix}") if images else None
    return video_path, cover, info


IMAGE_SUFFIXES = {".jpg", ".jpeg", ".webp", ".png", ".image", ".heic"}
