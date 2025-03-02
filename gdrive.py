import os
import pickle
import re
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
from io import BytesIO

# Scopes for Google Drive API
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

    def _create_folder(self, folder_name):
        """
        Create a folder in Google Drive if it doesn't exist.

        :param folder_name: Name of the folder to create.
        :return: ID of the folder.
        """
        query = f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder'"
        response = self.service.files().list(q=query, spaces='drive', fields='files(id)').execute()
        folders = response.get('files', [])

        if folders:
            return folders[0]['id']  # Folder already exists
        else:
            # Create the folder
            file_metadata = {
                'name': folder_name,
                'mimeType': 'application/vnd.google-apps.folder'
            }
            folder = self.service.files().create(body=file_metadata, fields='id').execute()
            return folder.get('id')

    def backup(self, local_file, folder_name='backup', remote_name=None):
        """
        Backup a file to Google Drive inside a specified folder.

        :param local_file: Path to the local file to upload.
        :param folder_name: Name of the folder in Google Drive (default: 'backup').
        :param remote_name: Name of the file on Google Drive (default: same as local file).
        :return: ID of the uploaded file or None if failed.
        """
        try:
            if not remote_name:
                remote_name = os.path.basename(local_file)

            # Create or get the folder ID
            folder_id = self._create_folder(folder_name)

            # Upload the file to the folder
            file_metadata = {
                'name': remote_name,
                'parents': [folder_id]  # Place the file inside the folder
            }
            media = MediaFileUpload(local_file)
            file = self.service.files().create(body=file_metadata, media_body=media, fields='id').execute()
            return file.get('id')
        except Exception as e:
            print(f"Backup failed: {e}")
            return None

    def restore(self, local_file, remote_name, folder_name='backup'):
        """
        Restore a file from Google Drive inside a specified folder.

        :param local_file: Path to save the downloaded file locally.
        :param remote_name: Name of the file on Google Drive.
        :param folder_name: Name of the folder in Google Drive (default: 'backup').
        :return: True if successful, False otherwise.
        """
        try:
            # Get the folder ID
            query = f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder'"
            response = self.service.files().list(q=query, spaces='drive', fields='files(id)').execute()
            folders = response.get('files', [])
            if not folders:
                print(f"No folder named '{folder_name}' found on Google Drive.")
                return False
            folder_id = folders[0]['id']

            # Search for the file inside the folder
            query = f"'{folder_id}' in parents"
            response = self.service.files().list(q=query, spaces='drive', fields='files(id, name)').execute()
            files = response.get('files', [])
            if not files:
                print(f"No file named '{remote_name}' found in folder '{folder_name}'.")
                return False

            # Download the file
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

def mainDrive():
    # Crear una instancia de la API
    gdrive = GDriveAPI()

    from datetime import datetime

    # Obtener la fecha y hora actual
    fecha_hora_actual = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    # Hacer un backup en la carpeta 'my_backups'
    #backup_id = gdrive.backup(local_file='pdvDB.sqlite', remote_name=f'pdvDB_backup_{fecha_hora_actual}.sqlite', folder_name='Punto de Venta (Respaldos)')
    #if backup_id:
    #    print(f"Backup successful! File ID: {backup_id}")
    
    # Restaurar un archivo desde la carpeta 'my_backups'
    restored = gdrive.restore(local_file='pdvDB.sqlite',  remote_name='pdvDB_backup', folder_name='Punto de Venta (Respaldos)')
    if restored:
        print("Restore successful!")

if __name__=='__main__':
	mainDrive()