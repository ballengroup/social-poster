"""social-poster: post once, repurpose everywhere.

  social-poster init      create config.yaml and the inbox folder
  social-poster run       process new videos in the inbox once
  social-poster watch     keep checking the inbox every few minutes
  social-poster amazon    walk through Amazon upload kits, one at a time
  social-poster status    show recent activity
"""

import argparse
import shutil
import subprocess
import sys
import time
import webbrowser
from pathlib import Path

from . import config as config_mod
from .db import History
from .destinations.amazon import AmazonKitDestination, mark_uploaded, pending_kits
from .destinations.tiktok import TikTokDraftDestination
from .pipeline import run_once
from .sources.folder import FolderSource


def _build(cfg):
    destinations = []
    if cfg["amazon"]["enabled"]:
        destinations.append(AmazonKitDestination(
            cfg["data_dir"] / "amazon_kits",
            only_hashtag=cfg["amazon"]["only_hashtag"],
            require_product_link=cfg["amazon"]["require_product_link"],
        ))
    if cfg["tiktok_publish"]["enabled"]:
        destinations.append(TikTokDraftDestination(cfg["tiktok_publish"]["access_token"]))
    if not destinations:
        sys.exit("Nothing to do: enable amazon and/or tiktok_publish in config.yaml")
    return FolderSource(cfg["inbox_dir"]), destinations, History(cfg["data_dir"] / "history.db")


def cmd_init(cfg, args):
    target = Path(args.config)
    if target.exists():
        print(f"{target} already exists, leaving it alone.")
    else:
        shutil.copy(Path(__file__).parent.parent / "config.example.yaml", target)
        print(f"Created {target}")
    cfg = config_mod.load(target)
    cfg["inbox_dir"].mkdir(parents=True, exist_ok=True)
    print(f"Drop videos (and optional same-name .txt captions) into: {cfg['inbox_dir'].resolve()}")


def cmd_run(cfg, args):
    source, destinations, history = _build(cfg)
    n = run_once(source, destinations, history)
    print(f"Done. {n} new post(s)." + _kit_hint(cfg))


def cmd_watch(cfg, args):
    source, destinations, history = _build(cfg)
    minutes = cfg["watch"]["interval_minutes"]
    print(f"Watching {cfg['inbox_dir']} every {minutes} min. Ctrl+C to stop.")
    while True:
        if run_once(source, destinations, history):
            print(_kit_hint(cfg).strip())
        time.sleep(minutes * 60)


def cmd_amazon(cfg, args):
    kits = pending_kits(cfg["data_dir"] / "amazon_kits")
    if not kits:
        print("No Amazon kits waiting. Nice.")
        return
    print(f"{len(kits)} video(s) ready for Amazon.\n")
    for i, (kit, info) in enumerate(kits, 1):
        print(f"--- {i}/{len(kits)} " + "-" * 40)
        print((kit / "UPLOAD.txt").read_text())
        _open_folder(kit)
        webbrowser.open(cfg["amazon"]["upload_url"])
        answer = input("Uploaded it? [y]es / [s]kip for now / [q]uit: ").strip().lower()
        if answer.startswith("y"):
            mark_uploaded(kit)
            print("Marked as uploaded.\n")
        elif answer.startswith("q"):
            return


def cmd_status(cfg, args):
    history = History(cfg["data_dir"] / "history.db")
    rows = history.recent(args.limit)
    if not rows:
        print("Nothing yet. Drop a video in the inbox and run `social-poster run`.")
    for when, source, sid, dest, status, detail in rows:
        print(f"{when}  {dest:<7} {status:<8} {sid}  {detail}")
    print(_kit_hint(cfg))


def _kit_hint(cfg) -> str:
    n = len(pending_kits(cfg["data_dir"] / "amazon_kits"))
    return f"\n{n} Amazon kit(s) waiting - run `social-poster amazon` to upload them." if n else ""


def _open_folder(path: Path) -> None:
    opener = {"darwin": "open", "win32": "explorer"}.get(sys.platform, "xdg-open")
    try:
        subprocess.Popen([opener, str(path)])
    except OSError:
        print(f"(Open this folder: {path})")


def main(argv=None):
    parser = argparse.ArgumentParser(prog="social-poster", description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--config", default="config.yaml")
    sub = parser.add_subparsers(dest="cmd", required=True)
    sub.add_parser("init").set_defaults(func=cmd_init)
    sub.add_parser("run").set_defaults(func=cmd_run)
    sub.add_parser("watch").set_defaults(func=cmd_watch)
    sub.add_parser("amazon").set_defaults(func=cmd_amazon)
    status = sub.add_parser("status")
    status.add_argument("--limit", type=int, default=25)
    status.set_defaults(func=cmd_status)
    args = parser.parse_args(argv)
    args.func(config_mod.load(args.config), args)


if __name__ == "__main__":
    main()
