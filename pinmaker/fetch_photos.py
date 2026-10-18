"""Download the photos from a blog post so pins can be designed from them.

Usage: python -m pinmaker.fetch_photos <post-url> [--out photos]

Writes <out>/<slug>/NN.jpg (largest available size of each in-post image, in page order)
plus meta.json with the post title, description and image sources.
"""

import argparse
import json
import re
import sys
from html.parser import HTMLParser
from io import BytesIO
from pathlib import Path
from urllib.parse import urljoin, urlparse
from urllib.request import Request, urlopen

from PIL import Image

UA = {"User-Agent": "Mozilla/5.0 (pinmaker; +https://github.com/ballengroup/social-poster)"}
MIN_SIDE = 500  # skip icons, logos, ad pixels
MAX_PHOTOS = 12
SIZE_SUFFIX = re.compile(r"-\d+x\d+(?=\.(?:jpe?g|png|webp)$)", re.I)


def fetch(url: str) -> bytes:
    with urlopen(Request(url, headers=UA), timeout=30) as r:
        return r.read()


class PageParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.meta: dict[str, str] = {}
        self.images: list[str] = []
        self.title = ""
        self._in_title = False

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "meta" and a.get("content"):
            key = a.get("property") or a.get("name")
            if key:
                self.meta[key] = a["content"]
        elif tag == "img":
            srcset = a.get("data-srcset") or a.get("srcset") or ""
            best = _largest_from_srcset(srcset) or a.get("data-src") or a.get("src")
            if best and not best.startswith("data:"):
                self.images.append(best)
        elif tag == "title":
            self._in_title = True

    def handle_endtag(self, tag):
        if tag == "title":
            self._in_title = False

    def handle_data(self, data):
        if self._in_title:
            self.title += data


def _largest_from_srcset(srcset: str) -> str | None:
    best, best_w = None, -1
    for part in srcset.split(","):
        bits = part.strip().split()
        if len(bits) == 2 and bits[1].endswith("w") and bits[1][:-1].isdigit():
            if int(bits[1][:-1]) > best_w:
                best, best_w = bits[0], int(bits[1][:-1])
    return best


def original_url(src: str) -> str:
    """WordPress serves resized copies as name-800x600.jpg; ask for the full-size file."""
    parsed = urlparse(src)
    path = SIZE_SUFFIX.sub("", parsed.path)
    return parsed._replace(path=path, query="").geturl()


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("url")
    ap.add_argument("--out", default="photos")
    args = ap.parse_args(argv)

    html = fetch(args.url).decode("utf-8", "replace")
    page = PageParser()
    page.feed(html)

    slug = urlparse(args.url).path.strip("/").split("/")[-1] or "post"
    out = Path(args.out) / slug
    out.mkdir(parents=True, exist_ok=True)

    candidates = []
    if page.meta.get("og:image"):
        candidates.append(page.meta["og:image"])
    candidates += page.images

    seen, saved = set(), []
    for src in candidates:
        src = urljoin(args.url, src)
        for url in dict.fromkeys([original_url(src), src]):  # full size first, then as-served
            key = SIZE_SUFFIX.sub("", urlparse(url).path)
            if key in seen:
                break
            try:
                im = Image.open(BytesIO(fetch(url)))
                im.load()
            except Exception:
                continue
            seen.add(key)
            if min(im.size) < MIN_SIDE:
                break
            name = f"{len(saved) + 1:02d}.jpg"
            im.convert("RGB").save(out / name, quality=92)
            saved.append({"file": name, "source": url, "size": im.size})
            break
        if len(saved) >= MAX_PHOTOS:
            break

    meta = {
        "url": args.url,
        "title": page.meta.get("og:title") or page.title.strip(),
        "description": page.meta.get("og:description") or page.meta.get("description", ""),
        "photos": saved,
    }
    (out / "meta.json").write_text(json.dumps(meta, indent=2, ensure_ascii=False) + "\n")
    print(f"Saved {len(saved)} photos to {out}")
    return 0 if saved else 1


if __name__ == "__main__":
    sys.exit(main())
