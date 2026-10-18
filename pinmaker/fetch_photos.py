"""Download the photos from blog posts so pins can be designed from them.

Usage: python -m pinmaker.fetch_photos <post-url> [<post-url> ...] [--out photos]

Amazon-hosted product images are skipped: Amazon's Associates rules don't allow reusing them on pins.

Writes <out>/<slug>/NN.jpg (largest available size of each in-post image, in page order)
plus meta.json with the post title, description and image sources.
"""

import argparse
import json
import re
import sys
import time
from html.parser import HTMLParser
from io import BytesIO
from pathlib import Path
from urllib.parse import urljoin, urlparse
from urllib.request import Request, urlopen

from PIL import Image

UA = {"User-Agent": "Mozilla/5.0 (pinmaker; +https://github.com/ballengroup/social-poster)"}
MIN_SIDE = 500  # skip icons, logos, ad pixels
MAX_PHOTOS = 12
AMAZON_HOSTS = ("media-amazon.com", "ssl-images-amazon.com", "images-amazon.com")
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


PHOTON_HOST = re.compile(r"^i\d\.wp\.com$")


def direct_url(src: str) -> str:
    """i0.wp.com/<site>/wp-content/... -> https://<site>/wp-content/... (Photon 404s on .webp files)."""
    parsed = urlparse(src)
    if PHOTON_HOST.match(parsed.hostname or ""):
        return "https://" + parsed.path.lstrip("/")
    return src


def is_amazon(url: str) -> bool:
    host = urlparse(url).hostname or ""
    return any(host.endswith(h) for h in AMAZON_HOSTS)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("urls", nargs="+")
    ap.add_argument("--out", default="photos")
    args = ap.parse_args(argv)

    failures = 0
    for url in args.urls:
        time.sleep(2)  # be gentle; the site starts refusing rapid-fire page loads
        try:
            if not fetch_post(url, Path(args.out)):
                failures += 1
        except Exception as e:  # one bad post shouldn't stop the batch
            print(f"{url}: FAILED {e}", file=sys.stderr)
            failures += 1
    return 1 if failures == len(args.urls) else 0


def featured_image(post_url: str) -> str | None:
    """Ask the WordPress.com API for the post's featured image (works when the page itself is blocked)."""
    parsed = urlparse(post_url)
    slug = parsed.path.strip("/").split("/")[-1]
    api = f"https://public-api.wordpress.com/wp/v2/sites/{parsed.hostname}/posts?slug={slug}&_embed=wp:featuredmedia"
    try:
        posts = json.loads(fetch(api))
        media = posts[0]["_embedded"]["wp:featuredmedia"][0]
        return media.get("source_url")
    except Exception as e:
        print(f"{post_url}: featured image lookup failed: {e}", file=sys.stderr)
        return None


def fetch_post(post_url: str, out_root: Path) -> int:
    try:
        html = fetch(post_url).decode("utf-8", "replace")
    except Exception as e:
        print(f"{post_url}: page fetch failed: {e}", file=sys.stderr)
        html = ""
    page = PageParser()
    page.feed(html)

    slug = urlparse(post_url).path.strip("/").split("/")[-1] or "post"
    out = out_root / slug
    out.mkdir(parents=True, exist_ok=True)

    # The API's featured image goes first: it reflects a new featured image right away,
    # while the page (and its og:image) can be served from cache for a while.
    candidates = []
    img = featured_image(post_url)
    if img:
        candidates.append(img)
    if page.meta.get("og:image"):
        candidates.append(page.meta["og:image"])
    candidates += page.images
    if not candidates or all(is_amazon(urljoin(post_url, c)) for c in candidates):
        img = featured_image(post_url)
        if img:
            candidates.append(img)

    seen, saved = set(), []
    for src in candidates:
        src = urljoin(post_url, src)
        if is_amazon(src):
            continue
        # full size from the site itself first, then the CDN copies
        for url in dict.fromkeys([direct_url(original_url(src)), original_url(src), src]):
            key = SIZE_SUFFIX.sub("", urlparse(url).path)
            if key in seen:
                break
            try:
                im = Image.open(BytesIO(fetch(url)))
                im.load()
            except Exception as e:
                print(f"  skip {url}: {e}", file=sys.stderr)
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
        "url": post_url,
        "title": page.meta.get("og:title") or page.title.strip(),
        "description": page.meta.get("og:description") or page.meta.get("description", ""),
        "photos": saved,
    }
    (out / "meta.json").write_text(json.dumps(meta, indent=2, ensure_ascii=False) + "\n")
    print(f"{post_url}: saved {len(saved)} photos to {out}")
    return len(saved)


if __name__ == "__main__":
    sys.exit(main())
