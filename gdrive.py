import os
import pickle
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
from io import BytesIO

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/drive']

class GDriveAPI:
    def __init__(self, credentials_file='credentials.json', token_file='token.pickle'):
        """
        Initialize the Google Drive API client.

        :param credentials_file: Path to the Google OAuth 2.0 credentials file.
        :param token_file: Path to the token file for storing user credentials.
        """
        self.credentials_file = credentials_file
        self.token_file = token_file

        # TODO: Comment this
        self.service = self._authenticate()

    def _authenticate(self):
        """
        Authenticate and return the Google Drive API service.

        :return: Google Drive API service object.
        """
        creds = None
        # Load existing credentials from the token file
        if os.path.exists(self.token_file):
            with open(self.token_file, 'rb') as token:
                creds = pickle.load(token)
        # If no valid credentials, prompt the user to log in
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(self.credentials_file, SCOPES)
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open(self.token_file, 'wb') as token:
                pickle.dump(creds, token)
        return build('drive', 'v3', credentials=creds)

    def backup(self, local_file, remote_name=None):
        """
        Backup a file to Google Drive.

        :param local_file: Path to the local file to upload.
        :param remote_name: Name of the file on Google Drive (default: same as local file).
        :return: ID of the uploaded file or None if failed.
        """
        try:
            if not remote_name:
                remote_name = os.path.basename(local_file)
            file_metadata = {'name': remote_name}
            media = MediaFileUpload(local_file)
            file = self.service.files().create(body=file_metadata, media_body=media, fields='id').execute()
            return file.get('id')
        except Exception as e:
            print(f"Backup failed: {e}")
            return None

    def restore(self, remote_name, local_file):
        """
        Restore a file from Google Drive.

        :param remote_name: Name of the file on Google Drive.
        :param local_file: Path to save the downloaded file locally.
        :return: True if successful, False otherwise.
        """
        try:
            # Search for the file on Google Drive
            response = self.service.files().list(q=f"name='{remote_name}'", spaces='drive', fields='files(id, name)').execute()
            files = response.get('files', [])
            if not files:
                print(f"No file named '{remote_name}' found on Google Drive.")
                return False

            # Download the first matching file
            file_id = files[0]['id']
            request = self.service.files().get_media(fileId=file_id)
            fh = BytesIO()
            downloader = MediaIoBaseDownload(fh, request)
            done = False
            while not done:
                status, done = downloader.next_chunk()
                print(f"Download {int(status.progress() * 100)}%.")

            # Save the downloaded file
            with open(local_file, 'wb') as f:
                f.write(fh.getvalue())
            return True
        except Exception as e:
            print(f"Restore failed: {e}")
            return False