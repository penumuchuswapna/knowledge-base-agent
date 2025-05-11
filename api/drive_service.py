from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import os

# If modifying these scopes, delete the token.json file.
SCOPES = ['https://www.googleapis.com/auth/drive.readonly']

def get_drive_service():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        flow = InstalledAppFlow.from_client_secrets_file(
            'credentials.json', SCOPES)
        creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    service = build('drive', 'v3', credentials=creds)
    return service

def search_docs(query_text):
    service = get_drive_service()
    results = service.files().list(
        q=f"name contains '{query_text}' and mimeType != 'application/vnd.google-apps.folder'",
        fields="files(id, name, mimeType)").execute()
    items = results.get('files', [])
    return items 