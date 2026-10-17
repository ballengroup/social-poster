"""Turns a TikTok description into an LTK-ready caption and pulls out product hints."""

import re

HASHTAG_RE = re.compile(r"#([\w぀-ヿ]+)", re.UNICODE)
MENTION_RE = re.compile(r"(?<![\w.])@([\w.]+)")
URL_RE = re.compile(r"https?://\S+")

# LTK captions get cut off in the feed; keep them tight.
MAX_CAPTION = 300


def split_hashtags(text: str) -> tuple[str, list[str]]:
    """Return (text without hashtags, hashtags in original order, deduped)."""
    tags = []
    for tag in HASHTAG_RE.findall(text):
        if tag.lower() not in (t.lower() for t in tags):
            tags.append(tag)
    body = HASHTAG_RE.sub("", text)
    body = re.sub(r"[ \t]+", " ", body)
    body = re.sub(r" *\n *", "\n", body)
    return body.strip(), tags


def build_ltk_caption(description: str, drop: list[str], add: list[str]) -> str:
    body, tags = split_hashtags(description or "")
    drop_set = {d.lower() for d in drop}
    keep = [t for t in tags if t.lower() not in drop_set]
    for extra in add:
        if extra.lower() not in (t.lower() for t in keep):
            keep.append(extra)

    tag_line = " ".join(f"#{t}" for t in keep)
    room = MAX_CAPTION - (len(tag_line) + 2 if tag_line else 0)
    if len(body) > room:
        body = body[: max(room - 1, 0)].rstrip() + "…"
    return f"{body}\n\n{tag_line}".strip() if tag_line else body


def product_hints(description: str) -> dict[str, list[str]]:
    """Things in the TikTok caption that point at products to tag in LTK."""
    text = description or ""
    return {
        "mentions": sorted(set(MENTION_RE.findall(text)), key=str.lower),
        "links": URL_RE.findall(text),
    }
