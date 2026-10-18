---
name: rolling-pins
description: Lori's rolling Pinterest pins for ballenblogger.com. Pick the next published post, have Tailwind design one pin in one of her three approved styles, show it to her, and schedule it only after she approves. Use when Lori says "next pin", "rolling pins", "pin the next post", or asks to keep the pin rotation going.
---

# Rolling pins (ballenblogger.com → Tailwind)

## Loop, one post at a time
1. **Next post.** List published posts on ballenblogger.com (WordPress.com connector, `posts.list`, newest first) and take the first one that has no pin yet in Tailwind (check `list_posts` drafts and queued for its URL).
2. **Design.** Tailwind `generate_pins_from_url` on account `1550127` (@ballenblogger) with `designTier: "premium"` and the next style in the rotation below. One generation per post. A URL that already has a SmartPin reuses its stored style, so the rotation only applies to posts Tailwind hasn't designed yet.
3. **Show Lori.** Fetch the image with `get_post_image`, send it to her with the title, description and the board you'd use. Point out any garbled letters (premium AI text sometimes mangles a letter, e.g. "ÐIY").
4. **Schedule only after she says yes** to that pin: `schedule_post` with the board and `useNextOpenSlot: true`. "Love these" about a set of samples is style feedback, not approval to post.
5. Move on to the next post.

## Approved styles (Lori's #1, #3, #5), rotate in this order
| # | `premiumStyle` | Look | Her sample |
|---|---|---|---|
| 1 | `image-highlight` | Full-bleed warm photo, white serif title over a dark fade at the bottom, pill-shaped url badge | Dried orange garland |
| 3 | `minimalist` | Cream background, dark brown serif title at top, soft props, gold pill url badge with sparkles | Apartment water filters |
| 5 | `professional` | Photo with a cream arched badge: bold sans title + script subtitle, compass ornament | Salt dough ornaments |

Not approved: `text-highlight`, `artistic`, `natural`, and the basic templates (random colors, product shots on white).

## Rules
- Never mark pins as AI-generated (no such field is sent). Don't try to hide AI imagery from Pinterest either.
- Never schedule without Lori's approval of that specific pin.
- Premium costs ~7 Tailwind credits per post. Check `get_account_usage` if unsure.

## Boards (ids from `list_boards`)
- Crafts to Make and Sell `830421687481303766`: craft/DIY posts about selling
- Gift Ideas `830421687481150087`
- Home Decor Ideas `830421687481074664`
- Cleaning Hacks `830421687481404831`
- Christmas `830421687481140408`, Halloween `830421687481148237`: seasonal
- Fun Crafts `830421687481172619`, Sewing `830421687481158516`, Recipes to Try `830421687481390211`, Skincare `830421687481404200`, Soap `830421687481387987`, DIY Jewelry `830421687481386342`
