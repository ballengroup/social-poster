"""Branded graphics for 'Stop Editing Your YouTube Videos' (The Real Time Creator).

All numbers come from Lori's V2 video transcript (Descript, Oct 21 2026).
Run: python3 make_graphics.py  -> writes JPGs next to this file.
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter, ImageFont

OUT = Path(__file__).parent
F = "/usr/share/fonts/opentype/inter/"
S = 2  # supersample

WHITE = (255, 255, 255)
TINT = (241, 235, 251)
PURPLE = (108, 63, 197)
PURPLE_L = (139, 92, 246)
GOLD = (245, 165, 36)
INK = (23, 21, 59)
MUTED = (110, 106, 140)
GREY = (200, 196, 214)


def font(name, size):
    return ImageFont.truetype(F + name, size * S)


def canvas(w=1600, h=1000):
    W, H = w * S, h * S
    img = Image.new("RGB", (W, H), WHITE)
    d = ImageDraw.Draw(img)
    for y in range(H):
        t = y / H
        c = tuple(int(WHITE[i] + (TINT[i] - WHITE[i]) * t) for i in range(3))
        d.line([(0, y), (W, y)], fill=c)
    m = 28 * S
    d.rounded_rectangle([m, m, W - m, H - m], radius=22 * S, outline=PURPLE, width=3 * S)
    return img, d


def header(d, kicker, headline, w=1600, size=64):
    x = 110 * S
    d.text((x, 96 * S), kicker, font=font("Inter-SemiBold.otf", 22), fill=PURPLE)
    d.text((x, 136 * S), headline, font=font("InterDisplay-Black.otf", size), fill=INK)
    y = 136 * S + int(size * 1.3) * S
    d.line([(x, y), (x + 140 * S, y)], fill=GOLD, width=4 * S)
    return y


def footer(d, note, w=1600, h=1000):
    x = 110 * S
    y = (h - 92) * S
    d.text((x, y), "The Real Time Creator · loriballen.substack.com",
           font=font("Inter-SemiBold.otf", 20), fill=INK)
    f = font("Inter-Regular.otf", 18)
    tw = d.textlength(note, font=f)
    d.text((w * S - x - tw, y + 2 * S), note, font=f, fill=MUTED)


def card(img, box, fill, radius=26):
    x0, y0, x1, y1 = [v * S for v in box]
    sh = Image.new("RGBA", img.size, (0, 0, 0, 0))
    sd = ImageDraw.Draw(sh)
    sd.rounded_rectangle([x0, y0 + 14 * S, x1, y1 + 14 * S], radius=radius * S,
                         fill=PURPLE + (60,))
    sh = sh.filter(ImageFilter.GaussianBlur(22 * S))
    img.paste(sh, (0, 0), sh)
    ImageDraw.Draw(img).rounded_rectangle([x0, y0, x1, y1], radius=radius * S, fill=fill)


def center(d, cx, y, text, f, fill):
    d.text((cx * S - d.textlength(text, font=f) / 2, y * S), text, font=f, fill=fill)


def save(img, name, w=1600, h=1000):
    img.resize((w, h), Image.LANCZOS).save(OUT / name, quality=94)


def cover():
    img, d = canvas()
    x = 110 * S
    d.text((x, 150 * S), "FROM MY VIDEO · THE REAL TIME CREATOR",
           font=font("Inter-SemiBold.otf", 24), fill=PURPLE)
    hf = font("InterDisplay-Black.otf", 104)
    d.text((x, 210 * S), "Stop editing", font=hf, fill=INK)
    d.text((x, 340 * S), "your YouTube", font=hf, fill=INK)
    d.text((x, 470 * S), "videos.", font=hf, fill=PURPLE)
    d.line([(x, 640 * S), (x + 160 * S, 640 * S)], fill=GOLD, width=5 * S)
    d.text((x, 680 * S), "One phone. One lapel mic. Twenty minutes of talking.",
           font=font("InterDisplay-Bold.otf", 36), fill=INK)
    d.text((x, 735 * S), "My whole talking-head system at 55.",
           font=font("Inter-Medium.otf", 30), fill=MUTED)
    footer(d, "Lori Ballen")
    save(img, "cover.jpg")


def sixteen():
    img, d = canvas()
    header(d, "WHY I KEEP CHANGING MY THUMBNAILS", "Same viewer. Same video. Up to 16 times.")
    card(img, (110, 330, 760, 790), PURPLE)
    center(d, 435, 380, "16", font("InterDisplay-Black.otf", 230), WHITE)
    center(d, 435, 650, "TIMES YOUTUBE MAY SHOW", font("Inter-SemiBold.otf", 24), GOLD)
    center(d, 435, 690, "ONE VIDEO TO ONE PERSON", font("Inter-SemiBold.otf", 24), GOLD)
    card(img, (840, 330, 1490, 790), WHITE)
    tx = 900
    d.text((tx * S, 380 * S), "So I'm testing:", font=font("InterDisplay-Bold.otf", 38), fill=INK)
    lines = ["They saw the thumbnail.", "They didn't click.", "They'll see it again.",
             "Change the thumbnail."]
    for i, t in enumerate(lines):
        y = 460 + i * 72
        d.ellipse([tx * S, (y + 12) * S, (tx + 16) * S, (y + 28) * S],
                  fill=GOLD if i == 3 else PURPLE_L)
        d.text(((tx + 36) * S, y * S), t, font=font("InterDisplay-Bold.otf" if i == 3 else "Inter-Medium.otf", 32),
               fill=PURPLE if i == 3 else INK)
    footer(d, "Per YouTube's CEO, as I heard it in an interview")
    save(img, "sixteen.jpg")


def best_video():
    img, d = canvas()
    header(d, "I ASKED CLAUDE + VIDIQ ONE QUESTION", "“What was my best video in the last 90 days?”", size=54)
    card(img, (110, 320, 900, 800), PURPLE)
    d.text((170 * S, 370 * S), "SELLING EVERYTHING AT 55 FOR TOTAL FREEDOM",
           font=font("Inter-SemiBold.otf", 22), fill=GOLD)
    d.text((165 * S, 430 * S), "133,850", font=font("InterDisplay-Black.otf", 180), fill=WHITE)
    d.text((170 * S, 660 * S), "VIEWS", font=font("Inter-SemiBold.otf", 28), fill=GOLD)
    d.text((170 * S, 705 * S), "Most watch time. Fastest pace.", font=font("Inter-Medium.otf", 28), fill=WHITE)
    card(img, (960, 320, 1490, 800), WHITE)
    center(d, 1225, 380, "~40%", font("InterDisplay-Black.otf", 150), PURPLE)
    center(d, 1225, 580, "MORE VIEWS THAN", font("Inter-SemiBold.otf", 24), INK)
    center(d, 1225, 620, "MY NUMBER TWO VIDEO", font("Inter-SemiBold.otf", 24), INK)
    center(d, 1225, 700, "Then: “Give me three more.”", font("Inter-Medium.otf", 26), MUTED)
    footer(d, "Data from my vidIQ account, pulled through Claude")
    save(img, "best-video.jpg")


def one_video():
    img, d = canvas()
    header(d, "ONE VIDEO, RUN THROUGH EVERYTHING", "I film it once. Claude does the rest.")
    steps = [("1", "Talk 20 min", "Phone, lapel mic,\nno B-roll"),
             ("15", "Shorts", "Descript + my\nClaude skill"),
             ("1", "Freebie", "Freedom number\nworksheet"),
             ("1", "Article", "Transcript into\nClaude")]
    cw, gap, x0, y0 = 320, 37, 110, 330
    for i, (num, label, sub) in enumerate(steps):
        x = x0 + i * (cw + gap)
        hero = i == 1
        card(img, (x, y0, x + cw, y0 + 460), PURPLE if hero else WHITE)
        cx = x + cw // 2
        center(d, cx, y0 + 40, num, font("InterDisplay-Black.otf", 170), WHITE if hero else PURPLE)
        center(d, cx, y0 + 250, label.upper(), font("Inter-SemiBold.otf", 28), GOLD if hero else INK)
        for j, ln in enumerate(sub.split("\n")):
            center(d, cx, y0 + 320 + j * 40, ln, font("Inter-Medium.otf", 26),
                   WHITE if hero else MUTED)
    footer(d, "My weekly long-form video workflow")
    save(img, "one-video.jpg")


if __name__ == "__main__":
    cover(); sixteen(); best_video(); one_video()
