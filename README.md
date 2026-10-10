# social-poster

Post once, then repurpose it everywhere. Drop a video in a folder, and social-poster:

- builds a ready-to-upload **Amazon Influencer kit** for it: the clean video file, a title made from
  your caption, the product ASINs pulled from your Amazon links, and a rule check
- optionally drops it into your **TikTok inbox as a draft** using TikTok's official Content Posting API
- remembers what it already handled, so nothing gets sent twice

## Staying inside Amazon's rules

Amazon has **no public API for Influencer video uploads**, and its Conditions of Use don't allow
robots or automated tools on the site. Because of that, **this tool never logs into or clicks around
amazon.com.** It does all the prep, and you do the upload in Creator Hub yourself. That takes about
30 seconds per video with the kit open.

It also avoids the things that commonly get videos rejected:

- **Use your originals.** The source is a folder of your own files, not videos downloaded from
  TikTok, so there are no TikTok watermarks and no scraping.
- **Rule check on every title.** It flags prices, promo codes, sale/deal language, "link in bio" and
  other off-Amazon calls to action, follow/subscribe asks, and mentions of other platforms.
- **In-video reminders.** Each kit lists the things a text check can't see: watermarks, prices said
  or shown on screen, music rights, and showing the product you tag.

Amazon's own Creator Hub guidelines are the final word. The checks are a safety net, not legal advice.

## Setup

```bash
python3 -m pip install -e .
social-poster init          # creates config.yaml and the inbox/ folder
```

Edit `config.yaml` (see `config.example.yaml` for every option).

## Daily use

1. Put the original video in `inbox/`. To pull a title and products from a caption, add a text file
   with the same name, e.g. `lamp.mp4` + `lamp.txt`. Paste your TikTok caption in it, including your
   Amazon link (`amazon.com/dp/...`, `amzn.to/...` and `a.co/...` all work).
2. Run `social-poster run`, or leave `social-poster watch` running.
3. Run `social-poster amazon`. For each waiting video it shows the kit, opens the kit folder and the
   Creator Hub upload page, and asks whether you uploaded it.

| Command | What it does |
|---|---|
| `social-poster run` | Process new videos in the inbox once |
| `social-poster watch` | Keep checking the inbox (every 5 min by default) |
| `social-poster amazon` | Walk through Amazon kits one at a time |
| `social-poster status` | Show recent activity |

### Filters

- `amazon.only_hashtag: amazonfinds` makes kits only for captions tagged `#amazonfinds`.
- `amazon.require_product_link: true` skips videos with no Amazon link in the caption.

### Optional: TikTok drafts

Set `tiktok_publish.enabled: true` and give it a user access token with the `video.upload` scope.
You can put it in the config or set `TIKTOK_ACCESS_TOKEN`. You'll need your own app at
developers.tiktok.com. Videos land in your TikTok inbox as drafts for you to finish and post.

## Development

```bash
python3 -m pip install -e '.[dev]'
python3 -m pytest
```
