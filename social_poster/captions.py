"""Turn a social caption into a clean title and a list of Amazon ASINs."""

import re

import requests

# ASINs are 10 chars, uppercase letters/digits, usually starting with B0.
_ASIN_IN_URL = re.compile(
    r"amazon\.[a-z.]+/(?:[^\s/]+/)?(?:dp|gp/product|gp/aw/d|product)/([A-Z0-9]{10})", re.I
)
_SHORT_LINK = re.compile(r"https?://(?:amzn\.to|a\.co)/[^\s]+", re.I)
_URL = re.compile(r"https?://\S+")
_HASHTAG = re.compile(r"(?:^|\s)#\w+")
_MENTION = re.compile(r"(?:^|\s)@[\w.]+")


def _resolve(url: str) -> str:
    try:
        return requests.head(url, allow_redirects=True, timeout=10).url
    except requests.RequestException:
        return url


def extract_asins(caption: str, resolve_short_links: bool = True) -> list[str]:
    """Find ASINs in amazon.com links, following amzn.to / a.co short links."""
    text = caption
    if resolve_short_links:
        for short in _SHORT_LINK.findall(caption):
            text += " " + _resolve(short)
    seen: list[str] = []
    for asin in _ASIN_IN_URL.findall(text):
        asin = asin.upper()
        if asin not in seen:
            seen.append(asin)
    return seen


def make_title(caption: str, max_len: int = 60) -> str:
    """Strip links, hashtags and @mentions; keep the first line of real words."""
    text = _URL.sub(" ", caption)
    text = _HASHTAG.sub(" ", text)
    text = _MENTION.sub(" ", text)
    lines = [" ".join(line.split()) for line in text.splitlines()]
    title = next((line for line in lines if line), "")
    if len(title) > max_len:
        title = title[:max_len].rsplit(" ", 1)[0].rstrip(",.;:-") + "…"
    return title


def has_hashtag(caption: str, tag: str) -> bool:
    tag = tag.lstrip("#").lower()
    return any(t.strip().lstrip("#").lower() == tag for t in _HASHTAG.findall(caption))
