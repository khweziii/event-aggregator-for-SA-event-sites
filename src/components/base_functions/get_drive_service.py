import os
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import pickle
import os 
from dotenv import load_dotenv


DRIVE_ID = os.environ.get("DRIVE_FOLDER_ID")

def get_drive_service_uri():

    load_dotenv()

    creds = None
    TOKEN_FILE = os.environ.get("TOKEN_FILE")
    # Instead of reading SCOPES from .env
    SCOPES = ["https://www.googleapis.com/auth/drive.file"]
    credentials_path = os.environ.get("OAUTH")
    # Load existing token if available
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, "rb") as token:
            creds = pickle.load(token)

    # If no valid credentials, log in
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(credentials_path, SCOPES)
            creds = flow.run_local_server(port=0)  # opens browser for login

        # Save token for future runs
        with open(TOKEN_FILE, "wb") as token:
            pickle.dump(creds, token)

    return build("drive", "v3", credentials=creds)


# if __name__ == "__main__":
#     service = get_drive_service()
#     print("✅ Drive service created successfully:", service)

