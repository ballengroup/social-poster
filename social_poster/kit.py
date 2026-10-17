"""Builds the per-video LTK prep kit folder."""

import json
import re
from pathlib import Path

from .caption import build_ltk_caption, product_hints
from .config import Config
from .tiktok import Video

CHECKLIST = """\
LTK upload checklist ({video_id})
================================

1. Open the LTK Creator app -> + -> Video.
2. Pick video{video_ext} from this folder (save it to your camera roll first if needed).
3. Cover: use {cover} if LTK asks for one.
4. Paste the caption from caption.txt.
5. Tag products. Hints from the TikTok caption are in products.txt.
6. Post, then delete this folder or move it to "Posted".

Original TikTok: {url}
"""


def kit_name(video: Video) -> str:
    date = video.uploaded.strftime("%Y-%m-%d") if video.uploaded else "undated"
    words = re.findall(r"[A-Za-z0-9]+", re.sub(r"#\S+", "", video.description))[:6]
    slug = "-".join(words).lower() or "video"
    return f"{date}_{slug}_{video.id}"


def write_kit(cfg: Config, video: Video, kit_dir: Path, video_path: Path, cover: Path | None) -> None:
    caption = build_ltk_caption(video.description, cfg.drop_hashtags, cfg.add_hashtags)
    hints = product_hints(video.description)

    (kit_dir / "caption.txt").write_text(caption + "\n")

    lines = ["Products to tag in LTK", "======================", ""]
    if hints["mentions"]:
        lines += ["Brands/accounts mentioned:"] + [f"  - @{m}" for m in hints["mentions"]] + [""]
    if hints["links"]:
        lines += ["Links in the caption:"] + [f"  - {u}" for u in hints["links"]] + [""]
    if not hints["mentions"] and not hints["links"]:
        lines += ["Nothing in the TikTok caption pointed to a product. Tag from memory or your LTK favorites.", ""]
    (kit_dir / "products.txt").write_text("\n".join(lines))

    (kit_dir / "CHECKLIST.txt").write_text(
        CHECKLIST.format(
            video_id=video.id,
            video_ext=video_path.suffix,
            cover=cover.name if cover else "(no cover saved, pick a frame in the app)",
            url=video.url,
        )
    )

    (kit_dir / "meta.json").write_text(
        json.dumps(
            {
                "tiktok_id": video.id,
                "tiktok_url": video.url,
                "uploaded": video.uploaded.isoformat() if video.uploaded else None,
                "original_description": video.description,
            },
            indent=2,
            ensure_ascii=False,
        )
        + "\n"
    )
