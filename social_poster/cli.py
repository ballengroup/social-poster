"""tiktok-to-ltk: find new TikToks and build LTK prep kits for them.

Usage:
    python -m social_poster              # process new videos
    python -m social_poster --dry-run    # just list what's new
    python -m social_poster --mark-all-done   # first run: skip your back catalog
    python -m social_poster --mark-all-done --keep-newest 1   # ...but leave the newest one for a sample kit
"""

import argparse
import shutil
import sys

from .config import load_config
from .drive import upload_kit
from .kit import kit_name, write_kit
from .state import State
from .tiktok import download, list_recent


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="social_poster", description=__doc__.splitlines()[0])
    parser.add_argument("--config", default="config.yaml")
    parser.add_argument("--dry-run", action="store_true", help="List new videos without downloading.")
    parser.add_argument(
        "--mark-all-done",
        action="store_true",
        help="Record every recent video as done without building kits (use once to skip old videos).",
    )
    parser.add_argument(
        "--keep-newest",
        type=int,
        default=0,
        metavar="N",
        help="With --mark-all-done, leave the N newest videos unmarked so the next run builds kits for them.",
    )
    args = parser.parse_args(argv)

    cfg = load_config(args.config)
    state = State(cfg.state_file)

    print(f"Checking @{cfg.tiktok_handle} (latest {cfg.check_latest})...")
    recent = list_recent(cfg.tiktok_handle, cfg.check_latest, cfg.tiktok_sec_uid)
    new = [v for v in recent if not state.is_done(v.id)]
    # Oldest first, so kits land in the order you posted them.
    new.sort(key=lambda v: v.uploaded.timestamp() if v.uploaded else 0)
    print(f"Found {len(recent)} recent, {len(new)} new.")

    if args.mark_all_done:
        if args.keep_newest:
            new = new[: -args.keep_newest]
        for v in new:
            state.mark_done(v.id, v.description[:80], kit_dir="(skipped)")
        print(f"Marked {len(new)} as done. Future runs only pick up videos posted after this.")
        return 0

    failures = 0
    for v in new:
        name = kit_name(v)
        print(f"- {name}")
        if args.dry_run:
            continue

        kit_dir = cfg.output_dir / name
        try:
            video_path, cover, _ = download(v, kit_dir)
            write_kit(cfg, v, kit_dir, video_path, cover)
            if cfg.gdrive_folder_id:
                print(f"  uploaded to Drive: {upload_kit(kit_dir, cfg.gdrive_folder_id)}")
        except Exception as e:  # keep going so one bad video doesn't block the rest
            failures += 1
            print(f"  FAILED: {e}", file=sys.stderr)
            shutil.rmtree(kit_dir, ignore_errors=True)
            continue

        state.mark_done(v.id, v.description[:80], str(kit_dir))
        print(f"  kit ready: {kit_dir}")

    return 1 if failures else 0
