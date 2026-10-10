"""Flag things in a title/caption that commonly get Amazon Influencer videos rejected.

These are warnings, not a legal check. Amazon's own Creator Hub guidelines are the
source of truth; this just catches the usual suspects before you upload.
"""

import re

_CHECKS = [
    (re.compile(r"https?://|www\.|\.com\b", re.I), "has a link or web address"),
    (re.compile(r"[$€£]\s?\d|\b\d+\s?(?:dollars|bucks)\b", re.I), "mentions a price"),
    (re.compile(r"\b(?:promo|coupon|discount)\s*code\b|\b\d{1,2}\s?% off\b", re.I), "mentions a promo/discount"),
    (re.compile(r"\b(?:sale|deal|prime day|black friday|cyber monday)\b", re.I), "mentions a sale or deal"),
    (re.compile(r"link in (?:my )?bio|\bcomment\b.+\b(?:link|send)\b|\bdm me\b", re.I), "has an off-Amazon call to action"),
    (re.compile(r"\b(?:follow|subscribe)\b", re.I), "asks people to follow/subscribe"),
    (re.compile(r"\b(?:tiktok|instagram|insta|\big\b|youtube|facebook|ltk|shopmy)\b", re.I), "names another platform"),
]


def check_text(text: str) -> list[str]:
    return [f'Title {msg}: "{text}"' for pattern, msg in _CHECKS if pattern.search(text)]


def review(title: str, asins: list[str]) -> list[str]:
    warnings = check_text(title)
    if not title:
        warnings.append("No title could be made from the caption - write one when you upload.")
    if not asins:
        warnings.append("No Amazon product link found in the caption - you'll need to tag the product by hand.")
    return warnings


# Shown on every kit. Things a text check can't see inside the video itself.
VIDEO_REMINDERS = [
    "Use your original file, with no TikTok/Instagram watermark or logo baked in.",
    "No prices, discount codes, or 'link in bio' said out loud or shown on screen.",
    "Music: only use audio you have rights to outside TikTok (TikTok's sound library doesn't carry over).",
    "Show the actual product you're tagging.",
]
