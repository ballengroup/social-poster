"""Amazon Influencer: build an upload kit. Never touches amazon.com on its own.

Amazon has no public upload API, and its Conditions of Use bar robots and automated
tools on the site. So this destination does all the prep (file, title, product
links, rule check) and the actual upload is done by you in Creator Hub.
"""

import json
import shutil
from pathlib import Path

from .. import compliance
from ..captions import extract_asins, has_hashtag, make_title
from ..models import PostResult, Video


class AmazonKitDestination:
    name = "amazon"

    def __init__(self, kits_dir: Path, only_hashtag: str = "", require_product_link: bool = False):
        self.kits_dir = kits_dir
        self.only_hashtag = only_hashtag
        self.require_product_link = require_product_link

    def wants(self, video: Video) -> tuple[bool, str]:
        if self.only_hashtag and not has_hashtag(video.caption, self.only_hashtag):
            return False, f"no #{self.only_hashtag.lstrip('#')} in caption"
        if self.require_product_link and not video.asins:
            return False, "no Amazon product link in caption"
        return True, ""

    def post(self, video: Video) -> PostResult:
        title = make_title(video.caption)
        warnings = compliance.review(title, video.asins)
        kit = self.kits_dir / video.source_id
        kit.mkdir(parents=True, exist_ok=True)
        dest = kit / f"video{video.path.suffix.lower()}"
        shutil.copy2(video.path, dest)

        info = {
            "id": video.source_id,
            "original_file": video.path.name,
            "video": dest.name,
            "title": title,
            "asins": video.asins,
            "product_links": [f"https://www.amazon.com/dp/{a}" for a in video.asins],
            "warnings": warnings,
            "uploaded": False,
        }
        (kit / "kit.json").write_text(json.dumps(info, indent=2))
        (kit / "UPLOAD.txt").write_text(render_instructions(info))
        note = f"kit ready ({len(warnings)} warning{'s' if len(warnings) != 1 else ''})"
        return PostResult(True, note)


def render_instructions(info: dict) -> str:
    lines = [
        "AMAZON INFLUENCER UPLOAD KIT",
        "",
        f"Video file : {info['video']}  (from {info['original_file']})",
        f"Title      : {info['title'] or '(write one)'}",
        "Products   : " + (", ".join(info["asins"]) or "(tag by hand)"),
    ]
    lines += [f"             {link}" for link in info["product_links"]]
    lines += ["", "Fix before uploading:" if info["warnings"] else "Rule check: nothing flagged."]
    lines += [f"  ! {w}" for w in info["warnings"]]
    lines += ["", "Double-check in the video itself:"]
    lines += [f"  - {r}" for r in compliance.VIDEO_REMINDERS]
    lines += [
        "",
        "Steps: open Creator Hub > Upload video, add the file, paste the title,",
        "tag the product(s), then save it as a draft or submit for review.",
    ]
    return "\n".join(lines) + "\n"


def pending_kits(kits_dir: Path) -> list[tuple[Path, dict]]:
    out = []
    for kit_json in sorted(kits_dir.glob("*/kit.json"), key=lambda p: p.stat().st_mtime):
        info = json.loads(kit_json.read_text())
        if not info.get("uploaded"):
            out.append((kit_json.parent, info))
    return out


def mark_uploaded(kit: Path) -> None:
    kit_json = kit / "kit.json"
    info = json.loads(kit_json.read_text())
    info["uploaded"] = True
    kit_json.write_text(json.dumps(info, indent=2))
