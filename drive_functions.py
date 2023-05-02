import io
import pickle
import os
from dotenv import load_dotenv
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from googleapiclient.http import MediaIoBaseDownload
from googleapiclient.http import MediaFileUpload

load_dotenv()
SCOPES = ["https://www.googleapis.com/auth/drive"]


def get_drive_service():
    """
    Initiate google drive API service using credentials.json
    """
    creds = None
    if os.path.exists("token.pickle"):
        with open("token.pickle", "rb") as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)
        with open("token.pickle", "wb") as token:
            pickle.dump(creds, token)
    return build("drive", "v3", credentials=creds)

def list_files(drive_service,page_size=1000,fields="nextPageToken, files(id, name, size, mimeType)",q=None,order_by='quotaBytesUsed desc'):
    """
    Returns a list of files including their id, name, size, and mimeType from Google drive, sorted by size
    """
    results = (
        drive_service.files()
        .list(
            pageSize=page_size,
            fields=fields,
            q=q,
            orderBy=order_by,
        )
        .execute()
    )
    return results.get("files", [])

def download_file(drive_service, file_id, file_name):
    """
    Downloads a file through drive_service using the file_id and file name
    """
    request = drive_service.files().get_media(fileId=file_id)
    file = io.BytesIO()
    downloader = MediaIoBaseDownload(file, request)
    done = False
    while done is False:
        status, done = downloader.next_chunk()
    file.seek(0)
    with open(file_name, "wb") as f:
        f.write(file.read())


def upload_file(drive_service, file_id, file_name, mime_type):
    media = MediaFileUpload(file_name, mimetype=mime_type)
    file = drive_service.files().update(fileId=file_id, media_body=media, fields="id").execute()



if __name__ == "__main__":
    drive_service = get_drive_service()

    results = (
        drive_service.files()
        .list(
            pageSize=1000,
            fields="nextPageToken, files(id, name, size, mimeType)",
            q="mimeType='text/plain'",
            orderBy="quotaBytesUsed desc",
        )
        .execute()
    )
    
    items = list_files(drive_service,q="mimeType='text/plain'")

    for i in items:
        if i['name'] == 'test_file.txt':
            file_info = i
            download_file(drive_service,i['id'],i['name'])
    
    with open(file_info['name'],'a') as f:
        f.write('\nand I appended this from python! Awesome!')
    
    upload_file(drive_service,file_info['id'],file_info['name'],file_info['mimeType'])