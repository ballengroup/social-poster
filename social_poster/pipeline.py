"""Send each new video in the inbox to every enabled destination, exactly once."""

from .captions import extract_asins
from .db import History

MAX_ATTEMPTS = 3


def run_once(source, destinations, history: History, log=print, resolve_short_links=True) -> int:
    """Process the inbox once. Returns how many destination posts succeeded."""
    sent = 0
    for video in source.scan():
        todo = [
            d for d in destinations
            if history.status(video.source, video.source_id, d.name) not in ("done", "skipped")
            and history.attempts(video.source, video.source_id, d.name) < MAX_ATTEMPTS
        ]
        if not todo:
            continue
        video.asins = extract_asins(video.caption, resolve_short_links=resolve_short_links)
        for dest in todo:
            wants = getattr(dest, "wants", None)
            if wants:
                ok, why = wants(video)
                if not ok:
                    history.record(video.source, video.source_id, dest.name, "skipped", why, video.caption)
                    log(f"[{dest.name}] skip {video.path.name}: {why}")
                    continue
            try:
                result = dest.post(video)
            except Exception as exc:  # one bad video shouldn't stop the rest
                result_ok, detail = False, f"{type(exc).__name__}: {exc}"
            else:
                result_ok, detail = result.ok, result.detail
            history.record(
                video.source, video.source_id, dest.name,
                "done" if result_ok else "failed", detail, video.caption,
            )
            log(f"[{dest.name}] {'ok' if result_ok else 'FAILED'} {video.path.name}: {detail}")
            sent += result_ok
    return sent
