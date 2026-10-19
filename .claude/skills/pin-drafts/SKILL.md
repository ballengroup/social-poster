---
name: pin-drafts
description: Lori's three-draft Pinterest routine for every ballenblogger.com post. For each URL, make a regular cream pin, an Ideogram pin and a black-and-white pop-of-color pin, and save all three as Tailwind drafts. When a post has no usable photo, make a magazine-worthy featured photo with Lori first. Use when Lori says "next url", "keep going", "make the pins", or asks for featured photos.
---

# Pin drafts (ballenblogger.com → Tailwind drafts)

Lori's taste lives in `pinmaker/PHOTO_STYLE.md`. Read it before every featured photo or Ideogram
pin, and add each new lesson to it right away ("learn as you go").

## Talking with Lori
- One thing at a time: show one image or ask one question, then wait.
- Always fix typos on her posts. Always improve: each round better than the last.

## Per post
1. **Photos.** Run the `fetch-pin-photos.yml` workflow with the post URL. It commits the photos to
   the `pin-photos` branch (the WordPress featured image comes first). Look at a contact sheet.
2. **No usable photo?** That means only text graphics (title baked in), Amazon images, or nothing.
   Make a featured photo:
   - Ideogram `edit_images`, `edit_nano_banana_pro`, 16:9, 2K, one image at a time.
   - Use a big, magazine-worthy idea shot like a real iPhone snapshot.
   - Iterate with Lori until she approves.
   - Then set it in WordPress: `media.create` with `source_url`, then `posts.update` `featured_media`.
   - Re-run the fetch workflow.
3. **Regular pin.** Cream design A or B from the scratch renderer, using her photo. Colors are
   matched to the photo (`photo_palette`), never plain blush.
4. **B&W pop pin.** Design D, a black-and-white photo with one color left in.
   - Pick a photo with a big, clearly saturated subject so the pop really pops.
   - Set `pop` when the automatic choice is wrong.
   - Pastel walls use `pop: "mint"` (low-saturation mode).
   - When the pop color also shows up in wood or skin, add `pop_box: [x0, y0, x1, y1]`
     (fractions of the photo) to keep the color to one subject.
5. **Ideogram pin.** `generate_images` `ideogram_3`, 2x3, realistic, magic off, quality, private.
   - Use the approved floating-label wording in PHOTO_STYLE.md word for word, with the label
     border, heart, script AND ballenblogger.com in colors taken from the photo.
   - Check the spelling with `describe_image`.
   - Create the draft with `mediaUrl`.
   - Eyeball it with `get_post_image`.
6. **Drafts.** Upload local images with `create_media_upload` + PUT, then call `create_post` with no
   schedule (that makes a draft). Account `1550127`. Write your own title, description, alt text
   and board.

## Rules
- Never use Amazon-hosted images (Amazon Associates TOS).
- Never mark pins as AI, and never strip metadata or screenshot to hide AI provenance.
- Drafts only. Never schedule without Lori's approval.
