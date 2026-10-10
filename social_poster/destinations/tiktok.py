"""Send a local video to your TikTok inbox as a draft (Content Posting API, video.upload scope).

TikTok then notifies you in the app to finish editing and post it.
Docs: https://developers.tiktok.com/doc/content-posting-api-reference-upload-video
"""

import math

import requests

from ..models import PostResult, Video

INIT_URL = "https://open.tiktokapis.com/v2/post/publish/inbox/video/init/"
MIN_CHUNK = 5 * 1024 * 1024
CHUNK = 10 * 1024 * 1024


def chunk_plan(size: int) -> tuple[int, int]:
    """TikTok wants floor(size/chunk) chunks; the last chunk carries the remainder."""
    if size <= MIN_CHUNK:
        return size, 1
    chunk = min(CHUNK, size)
    return chunk, max(1, math.floor(size / chunk))


class TikTokDraftDestination:
    name = "tiktok"

    def __init__(self, access_token: str):
        if not access_token:
            raise ValueError("No TikTok access token (tiktok_publish.access_token or TIKTOK_ACCESS_TOKEN)")
        self.token = access_token

    def post(self, video: Video) -> PostResult:
        data = video.path.read_bytes()
        size = len(data)
        chunk, count = chunk_plan(size)
        resp = requests.post(
            INIT_URL,
            headers={"Authorization": f"Bearer {self.token}", "Content-Type": "application/json"},
            json={
                "source_info": {
                    "source": "FILE_UPLOAD",
                    "video_size": size,
                    "chunk_size": chunk,
                    "total_chunk_count": count,
                }
            },
            timeout=30,
        )
        body = resp.json()
        if body.get("error", {}).get("code") not in (None, "ok"):
            return PostResult(False, f"TikTok init failed: {body['error']}")
        upload_url = body["data"]["upload_url"]
        publish_id = body["data"]["publish_id"]

        for i in range(count):
            start = i * chunk
            end = size if i == count - 1 else start + chunk
            put = requests.put(
                upload_url,
                headers={
                    "Content-Type": "video/mp4",
                    "Content-Range": f"bytes {start}-{end - 1}/{size}",
                },
                data=data[start:end],
                timeout=300,
            )
            if put.status_code not in (200, 201, 206):
                return PostResult(False, f"TikTok chunk {i + 1}/{count} failed: HTTP {put.status_code}")
        return PostResult(True, f"in TikTok inbox as draft (publish_id {publish_id})")
