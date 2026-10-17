import json
from datetime import datetime, timezone
from pathlib import Path

import pytest

from social_poster import cli
from social_poster.caption import MAX_CAPTION, build_ltk_caption, product_hints
from social_poster.kit import kit_name
from social_poster.tiktok import Video

DESC = "Obsessed with this linen set from @abercrombie 😍 link in bio #fyp #ootd #summerstyle #FYP #tiktokmademebuyit"


def test_caption_drops_tiktok_tags_and_keeps_the_rest():
    caption = build_ltk_caption(DESC, drop=["fyp", "tiktokmademebuyit"], add=["LTKstyletip"])
    assert caption == (
        "Obsessed with this linen set from @abercrombie 😍 link in bio\n\n#ootd #summerstyle #LTKstyletip"
    )


def test_caption_is_trimmed_but_keeps_hashtags():
    caption = build_ltk_caption("word " * 200 + "#ootd", drop=[], add=[])
    assert len(caption) <= MAX_CAPTION
    assert caption.endswith("#ootd")
    assert "…" in caption


def test_caption_without_hashtags():
    assert build_ltk_caption("just a dress", drop=["fyp"], add=[]) == "just a dress"


def test_product_hints():
    hints = product_hints(DESC + " https://shop.example.com/x and @Target.style")
    assert hints == {"mentions": ["abercrombie", "Target.style"], "links": ["https://shop.example.com/x"]}


def test_kit_name():
    v = Video("123", "u", "Fall porch decor ideas you need! #fall #decor", datetime(2026, 10, 1, tzinfo=timezone.utc))
    assert kit_name(v) == "2026-10-01_fall-porch-decor-ideas-you-need_123"


@pytest.fixture
def project(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    Path("config.yaml").write_text("tiktok_handle: '@lori'\ndrop_hashtags: [fyp]\n")
    old = Video("1", "https://t/1", "old one #fyp", datetime(2026, 9, 1, tzinfo=timezone.utc))
    new = Video("2", "https://t/2", "New mug @anthropologie #fyp #coffee", datetime(2026, 10, 2, tzinfo=timezone.utc))
    monkeypatch.setattr(cli, "list_recent", lambda handle, limit, sec_uid: [new, old])

    def fake_download(video, dest):
        dest.mkdir(parents=True)
        (dest / "video.mp4").write_bytes(b"mp4")
        (dest / "cover.jpg").write_bytes(b"jpg")
        return dest / "video.mp4", dest / "cover.jpg", {}

    monkeypatch.setattr(cli, "download", fake_download)
    return tmp_path


def test_first_run_with_mark_all_done_skips_back_catalog(project):
    assert cli.main(["--mark-all-done"]) == 0
    assert set(json.loads(Path("state.json").read_text())["done"]) == {"1", "2"}
    assert not Path("kits").exists()


def test_builds_kits_only_for_new_videos(project):
    Path("state.json").write_text(json.dumps({"done": {"1": {}}}))
    assert cli.main([]) == 0

    kits = list(Path("kits").iterdir())
    assert [k.name for k in kits] == ["2026-10-02_new-mug-anthropologie_2"]
    kit = kits[0]
    assert (kit / "caption.txt").read_text() == "New mug @anthropologie\n\n#coffee\n"
    assert "@anthropologie" in (kit / "products.txt").read_text()
    assert "video.mp4" in (kit / "CHECKLIST.txt").read_text()
    assert "2" in json.loads(Path("state.json").read_text())["done"]

    # Second run finds nothing new.
    assert cli.main([]) == 0
    assert len(list(Path("kits").iterdir())) == 1


def test_failed_download_is_retried_next_run(project, monkeypatch):
    def boom(video, dest):
        dest.mkdir(parents=True)
        raise RuntimeError("TikTok said no")

    monkeypatch.setattr(cli, "download", boom)
    assert cli.main([]) == 1
    assert not any(Path("kits").iterdir())
    assert not Path("state.json").exists()  # nothing marked done, so both videos retry next run
