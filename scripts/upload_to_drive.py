import json
import os
import sys
from pathlib import Path

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

SCOPES = ["https://www.googleapis.com/auth/drive"]
MIME_CSV = "text/csv"
MIME_TXT = "text/plain"
MIME_FOLDER = "application/vnd.google-apps.folder"


def authenticate():
    creds_json = os.environ.get("GDRIVE_SA_CREDENTIALS")
    if not creds_json:
        print("ERROR: GDRIVE_SA_CREDENTIALS not set.")
        sys.exit(1)
    info = json.loads(creds_json)
    creds = service_account.Credentials.from_service_account_info(info, scopes=SCOPES)
    return build("drive", "v3", credentials=creds)


def find_or_create_folder(service, name, parent_id):
    query = (
        f"name = '{name}' and '{parent_id}' in parents "
        f"and mimeType = '{MIME_FOLDER}' and trashed = false"
    )
    results = service.files().list(q=query, fields="files(id)").execute()
    files = results.get("files", [])
    if files:
        return files[0]["id"]

    metadata = {
        "name": name,
        "mimeType": MIME_FOLDER,
        "parents": [parent_id],
    }
    folder = service.files().create(body=metadata, fields="id").execute()
    print(f"  [CREATED FOLDER] {name}")
    return folder["id"]


def ensure_folder_path(service, root_id, folder_parts):
    current_id = root_id
    for part in folder_parts:
        current_id = find_or_create_folder(service, part, current_id)
    return current_id


def upload_file(service, local_path, parent_id):
    name = local_path.name
    mime = MIME_CSV if name.endswith(".csv") else MIME_TXT

    query = (
        f"name = '{name}' and '{parent_id}' in parents "
        f"and trashed = false"
    )
    results = service.files().list(q=query, fields="files(id)").execute()
    existing = results.get("files", [])

    media = MediaFileUpload(str(local_path), mimetype=mime)

    if existing:
        file_id = existing[0]["id"]
        service.files().update(fileId=file_id, media_body=media).execute()
        print(f"  [UPDATED] {name}")
    else:
        metadata = {"name": name, "parents": [parent_id]}
        service.files().create(body=metadata, media_body=media, fields="id").execute()
        print(f"  [UPLOADED] {name}")


def main():
    root_folder_id = os.environ.get("GDRIVE_FOLDER_ID")
    if not root_folder_id:
        print("ERROR: GDRIVE_FOLDER_ID not set.")
        sys.exit(1)

    coletas_dir = Path("coletas")
    if not coletas_dir.is_dir():
        print("ERROR: coletas/ directory not found.")
        sys.exit(1)

    files_to_upload = [
        f for f in coletas_dir.rglob("*")
        if f.is_file() and f.name != ".gitkeep" and (f.suffix in (".csv", ".txt"))
    ]

    if not files_to_upload:
        print("No files to upload.")
        return

    print(f"Found {len(files_to_upload)} file(s) to upload.")
    service = authenticate()

    for file_path in sorted(files_to_upload):
        rel = file_path.relative_to(coletas_dir)
        folder_parts = list(rel.parent.parts)

        print(f"\n[FILE] {rel}")
        parent_id = ensure_folder_path(service, root_folder_id, folder_parts)
        upload_file(service, file_path, parent_id)

    print(f"\nDone. Uploaded {len(files_to_upload)} file(s).")


if __name__ == "__main__":
    main()
