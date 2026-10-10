import json

from social_poster import compliance
from social_poster.captions import extract_asins, has_hashtag, make_title
from social_poster.db import History
from social_poster.destinations.amazon import AmazonKitDestination, mark_uploaded, pending_kits
from social_poster.destinations.tiktok import chunk_plan
from social_poster.models import PostResult
from social_poster.pipeline import run_once
from social_poster.sources.folder import FolderSource

CAPTION = (
    "This lamp changed my desk setup ✨\n"
    "https://www.amazon.com/Some-Lamp/dp/B0ABCDE123?tag=x https://amazon.com/gp/product/b0zzzzzzz9 "
    "#amazonfinds #desksetup @someone"
)


def test_extract_asins_dedupes_and_uppercases():
    caption = CAPTION + " https://www.amazon.com/dp/B0ABCDE123"
    assert extract_asins(caption, resolve_short_links=False) == ["B0ABCDE123", "B0ZZZZZZZ9"]


def test_make_title_strips_links_tags_mentions():
    assert make_title(CAPTION) == "This lamp changed my desk setup ✨"
    assert make_title("#onlytags #here\nreal words here") == "real words here"
    assert make_title("word " * 30).endswith("…")


def test_has_hashtag():
    assert has_hashtag(CAPTION, "#AmazonFinds")
    assert not has_hashtag(CAPTION, "amazon")


def test_compliance_flags_common_problems():
    flagged = " ".join(compliance.check_text("Only $19 with promo code LORI, link in bio, follow on TikTok"))
    for phrase in ("price", "promo", "call to action", "follow", "another platform"):
        assert phrase in flagged
    assert compliance.check_text("This lamp changed my desk setup") == []
    assert any("product" in w for w in compliance.review("Nice lamp", []))


def test_tiktok_chunk_plan():
    assert chunk_plan(3_000_000) == (3_000_000, 1)
    chunk, count = chunk_plan(25 * 1024 * 1024)
    assert chunk == 10 * 1024 * 1024 and count == 2  # last chunk carries the extra 5MB


class FakeDest:
    name = "fake"

    def __init__(self, fail=False):
        self.calls, self.fail = [], fail

    def post(self, video):
        self.calls.append(video.source_id)
        if self.fail:
            raise RuntimeError("boom")
        return PostResult(True, "ok")


def _inbox(tmp_path):
    inbox = tmp_path / "inbox"
    inbox.mkdir()
    (inbox / "lamp.mp4").write_bytes(b"fake video 1")
    (inbox / "lamp.txt").write_text(CAPTION)
    (inbox / "mug.mov").write_bytes(b"fake video 2")
    (inbox / "notes.pdf").write_bytes(b"ignored")
    return inbox


def test_pipeline_posts_each_video_once(tmp_path):
    source = FolderSource(_inbox(tmp_path))
    dest, history = FakeDest(), History(tmp_path / "h.db")
    assert run_once(source, [dest], history, log=lambda *_: None, resolve_short_links=False) == 2
    assert run_once(source, [dest], history, log=lambda *_: None, resolve_short_links=False) == 0
    assert len(dest.calls) == 2


def test_pipeline_gives_up_after_three_failures(tmp_path):
    source = FolderSource(_inbox(tmp_path))
    dest, history = FakeDest(fail=True), History(tmp_path / "h.db")
    for _ in range(5):
        run_once(source, [dest], history, log=lambda *_: None, resolve_short_links=False)
    assert len(dest.calls) == 2 * 3


def test_amazon_kit_end_to_end(tmp_path):
    source = FolderSource(_inbox(tmp_path))
    kits_dir = tmp_path / "kits"
    amazon = AmazonKitDestination(kits_dir, only_hashtag="amazonfinds")
    history = History(tmp_path / "h.db")
    run_once(source, [amazon], history, log=lambda *_: None, resolve_short_links=False)

    kits = pending_kits(kits_dir)
    assert len(kits) == 1  # mug.mov has no #amazonfinds caption, so it's skipped
    kit, info = kits[0]
    assert info["title"] == "This lamp changed my desk setup ✨"
    assert info["asins"] == ["B0ABCDE123", "B0ZZZZZZZ9"]
    assert (kit / "video.mp4").read_bytes() == b"fake video 1"
    assert "B0ABCDE123" in (kit / "UPLOAD.txt").read_text()
    statuses = {r[4] for r in history.recent()}
    assert statuses == {"done", "skipped"}

    mark_uploaded(kit)
    assert pending_kits(kits_dir) == []
    assert json.loads((kit / "kit.json").read_text())["uploaded"] is True
