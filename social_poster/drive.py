"""Optional: copies a kit folder into Google Drive so it's on your phone."""

import mimetypes
import os
from pathlib import Path


def upload_kit(kit_dir: Path, parent_folder_id: str) -> str:
    """Upload kit_dir as a subfolder of parent_folder_id. Returns the new folder's URL."""
    from google.oauth2 import service_account
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaFileUpload

    creds_path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
    if not creds_path:
        raise SystemExit("GDRIVE_FOLDER_ID is set but GOOGLE_APPLICATION_CREDENTIALS isn't.")
    creds = service_account.Credentials.from_service_account_file(
        creds_path, scopes=["https://www.googleapis.com/auth/drive"]
    )
    drive = build("drive", "v3", credentials=creds, cache_discovery=False)

    folder = (
        drive.files()
        .create(
            body={
                "name": kit_dir.name,
                "mimeType": "application/vnd.google-apps.folder",
                "parents": [parent_folder_id],
            },
            fields="id, webViewLink",
            supportsAllDrives=True,
        )
        .execute()
    )

    for path in sorted(kit_dir.iterdir()):
        if not path.is_file():
            continue
        mime = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
        drive.files().create(
            body={"name": path.name, "parents": [folder["id"]]},
            media_body=MediaFileUpload(str(path), mimetype=mime, resumable=True),
            fields="id",
            supportsAllDrives=True,
        ).execute()

    return folder["webViewLink"]
