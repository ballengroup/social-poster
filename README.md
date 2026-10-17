# social-poster

## TikTok → LTK prep kits

LTK has no public posting API, so this tool does everything except the final tap. It watches your
TikTok profile, and for each **new** video it builds a kit folder:

```
kits/2026-10-02_fall-porch-decor-ideas_7351234567890/
  video.mp4       clean download (non-watermarked version when TikTok offers one)
  cover.jpg       TikTok's cover frame
  caption.txt     LTK-ready caption: TikTok-only hashtags (#fyp etc.) removed, your LTK tags added
  products.txt    brands (@mentions) and links from the caption, to help you tag products
  CHECKLIST.txt   the 60-second upload steps for the LTK Creator app
  meta.json       original TikTok URL, date and caption
```

If you set a Google Drive folder, each kit is also uploaded there, so it's on your phone when you
open the LTK app.

### Run it on your computer

```bash
pip install -r requirements.txt
cp config.example.yaml config.yaml      # set tiktok_handle
python -m social_poster --mark-all-done # first time only: skip your existing videos
python -m social_poster --dry-run       # see what's new
python -m social_poster                 # build kits
```

Leave out `--mark-all-done` on the first run if you want kits for your recent back catalog too
(up to `check_latest` videos).

Tip: point `output_dir` at a folder inside Google Drive for desktop or iCloud Drive and the kits
sync to your phone without the Drive API setup below.

### Run it daily on GitHub (optional)

`.github/workflows/tiktok-to-ltk.yml` runs every morning and on demand (Actions → *TikTok to LTK
kits* → *Run workflow*). In the repo settings:

| Setting | Where | Value |
| --- | --- | --- |
| `TIKTOK_HANDLE` | Variables | your handle, no `@` |
| `TIKTOK_SEC_UID` | Variables | optional, see troubleshooting |
| `GDRIVE_FOLDER_ID` | Secrets | ID at the end of the Drive folder URL |
| `GDRIVE_SERVICE_ACCOUNT_JSON` | Secrets | the service account key file's contents |

Drive setup: in Google Cloud, create a service account, enable the Drive API, download a JSON key,
then share your Drive folder with the service account's email as **Editor**. Without Drive, kits
are still downloadable from each workflow run's *Artifacts* for 14 days.

The workflow commits `state.json` after each run so it remembers what's done.

### Troubleshooting

- **"Unable to extract secondary user ID"**: TikTok blocked the profile lookup (common from cloud
  servers like GitHub Actions). Set `tiktok_sec_uid` to your secUid. To find it, open your profile
  in a desktop browser, view the page source, and search for `"secUid":"`. It's the long string
  after that. If TikTok keeps blocking GitHub's servers, run the tool on your own computer instead.
- **Video still has a watermark**: TikTok didn't offer a clean version for that video. Swap in the
  original file from your camera roll (TikTok's own "Save video" adds a watermark too).
- A video that fails isn't marked done, so it's retried on the next run.

### Tests

```bash
pip install pytest && python -m pytest
```
