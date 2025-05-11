from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import os

SCOPES = ['https://www.googleapis.com/auth/drive.readonly']
REDIRECT_URI = 'http://localhost:8081/'

def get_drive_service():
    try:
        creds = None
        if os.path.exists('token.json'):
            creds = Credentials.from_authorized_user_file('token.json', SCOPES)
        if not creds or not creds.valid:
            if not os.path.exists('credentials.json'):
                raise FileNotFoundError("credentials.json not found. Please download it from Google Cloud Console.")
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', 
                SCOPES,
                redirect_uri=REDIRECT_URI
            )
            creds = flow.run_local_server(port=8081)
            with open('token.json', 'w') as token:
                token.write(creds.to_json())
        service = build('drive', 'v3', credentials=creds)
        return service
    except Exception as e:
        print(f"Error in get_drive_service: {str(e)}")
        raise

def search_drive_files(query_text):
    try:
        service = get_drive_service()
        results = service.files().list(
            q=f"name contains '{query_text}' and mimeType != 'application/vnd.google-apps.folder'",
            fields="files(id, name, mimeType)").execute()
        return results.get('files', [])
    except Exception as e:
        print(f"Error in search_drive_files: {str(e)}")
        raise 