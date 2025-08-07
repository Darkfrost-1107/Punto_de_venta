import os
import json
import requests
from datetime import datetime
from kivy.utils import platform

class GDriveAPI:
    def __init__(self, credentials_file='credentials.json', token_file='token.json'):
        """
        Initialize the Google Drive API client - Compatible con Android.

        :param credentials_file: Path to the Google OAuth 2.0 credentials file (JSON con access_token).
        :param token_file: Path to the token file for storing user credentials.
        
        NOTA PARA ANDROID: 
        - credentials_file debe contener: {"access_token": "tu_token", "api_key": "tu_api_key"}
        - Obtener access_token desde: https://developers.google.com/oauthplayground/
        - Scope necesario: https://www.googleapis.com/auth/drive
        """
        self.credentials_file = credentials_file
        self.token_file = token_file
        
        # Configurar rutas según la plataforma
        if platform == 'android':
            try:
                from android.storage import app_storage_path
                self.storage_path = app_storage_path()
            except ImportError:
                # Fallback para testing
                self.storage_path = '/data/data/org.kivy.android/files'
        else:
            self.storage_path = '.'
        
        # Actualizar rutas de archivos
        if not os.path.isabs(self.credentials_file):
            self.credentials_file = os.path.join(self.storage_path, self.credentials_file)
        if not os.path.isabs(self.token_file):
            self.token_file = os.path.join(self.storage_path, self.token_file)
            
        self.service = self._authenticate()
        self.base_url = "https://www.googleapis.com/drive/v3"

    def _authenticate(self):
        """
        Authenticate and return the Google Drive API service - Versión Android.

        :return: Dict con credenciales o None si falla.
        """
        creds = None
        
        # Load existing credentials from the token file
        if os.path.exists(self.token_file):
            try:
                with open(self.token_file, 'r') as token:
                    creds = json.load(token)
                print("Loaded existing token")
            except Exception as e:
                print(f"Error loading token: {e}")
        
        # If no valid credentials, load from credentials file
        if not creds or not self._is_token_valid(creds):
            if os.path.exists(self.credentials_file):
                try:
                    with open(self.credentials_file, 'r') as cred_file:
                        creds = json.load(cred_file)
                    
                    # Save the credentials for the next run
                    try:
                        with open(self.token_file, 'w') as token:
                            json.dump(creds, token)
                        print("Saved new token")
                    except Exception as e:
                        print(f"Error saving token: {e}")
                        
                except Exception as e:
                    print(f"Error loading credentials: {e}")
                    return None
            else:
                print(f"Credentials file not found: {self.credentials_file}")
                print("Create credentials.json with: {'access_token': 'your_token', 'api_key': 'your_key'}")
                return None
        
        return creds

    def _is_token_valid(self, creds):
        """
        Verificar si el token sigue siendo válido haciendo una llamada de prueba.
        
        :param creds: Credenciales a verificar
        :return: True si válido, False si no
        """
        if not creds:
            return False
            
        try:
            # Test simple call to verify token
            headers = self._get_headers(creds)
            response = requests.get(f"{self.base_url}/about", headers=headers, timeout=5)
            return response.status_code == 200
        except:
            return False

    def _get_headers(self, creds=None):
        """
        Obtener headers para autenticación.
        
        :param creds: Credenciales (usa self.service si no se proporciona)
        :return: Dict con headers
        """
        if not creds:
            creds = self.service
            
        if not creds:
            raise Exception("No credentials available")
            
        if 'access_token' in creds:
            return {'Authorization': f'Bearer {creds["access_token"]}'}
        else:
            raise Exception("No access token in credentials")

    def _get_params(self, creds=None):
        """
        Obtener parámetros para API key (fallback).
        
        :param creds: Credenciales
        :return: Dict con parámetros
        """
        if not creds:
            creds = self.service
            
        if creds and 'api_key' in creds and 'access_token' not in creds:
            return {'key': creds['api_key']}
        return {}

    def _create_folder(self, folder_name):
        """
        Create a folder in Google Drive if it doesn't exist - Versión Android.

        :param folder_name: Name of the folder to create.
        :return: ID of the folder.
        """
        try:
            # Search for existing folder
            headers = self._get_headers()
            params = self._get_params()
            
            query = f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder' and trashed=false"
            params['q'] = query
            params['fields'] = 'files(id,name)'
            
            response = requests.get(f"{self.base_url}/files", headers=headers, params=params, timeout=10)
            
            if response.status_code == 200:
                folders = response.json().get('files', [])
                if folders:
                    print(f"Folder '{folder_name}' already exists")
                    return folders[0]['id']  # Folder already exists
            
            # Create the folder
            headers['Content-Type'] = 'application/json'
            file_metadata = {
                'name': folder_name,
                'mimeType': 'application/vnd.google-apps.folder'
            }
            
            response = requests.post(f"{self.base_url}/files", 
                                   headers=headers, 
                                   json=file_metadata, 
                                   timeout=10)
            
            if response.status_code == 200:
                folder_id = response.json().get('id')
                print(f"Created folder '{folder_name}' with ID: {folder_id}")
                return folder_id
            else:
                print(f"Error creating folder: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            print(f"Error in _create_folder: {e}")
            return None

    def backup(self, local_file, folder_name='backup', remote_name=None):
        """
        Backup a file to Google Drive inside a specified folder - Versión Android.

        :param local_file: Path to the local file to upload.
        :param folder_name: Name of the folder in Google Drive (default: 'backup').
        :param remote_name: Name of the file on Google Drive (default: same as local file).
        :return: ID of the uploaded file or None if failed.
        """
        try:
            if not self.service:
                print("Authentication failed - cannot backup")
                return None
                
            # Verificar que el archivo existe
            if not os.path.isabs(local_file):
                local_file = os.path.join(self.storage_path, local_file)
                
            if not os.path.exists(local_file):
                print(f"Local file not found: {local_file}")
                return None

            if not remote_name:
                remote_name = os.path.basename(local_file)

            # Create or get the folder ID
            folder_id = self._create_folder(folder_name)
            if not folder_id:
                print(f"Failed to create/find folder: {folder_name}")
                return None

            # Preparar metadata del archivo
            file_metadata = {
                'name': remote_name,
                'parents': [folder_id]  # Place the file inside the folder
            }

            # Upload usando multipart
            url = "https://www.googleapis.com/upload/drive/v3/files?uploadType=multipart"
            headers = {'Authorization': f'Bearer {self.service["access_token"]}'}

            # Leer archivo y preparar multipart
            with open(local_file, 'rb') as file_data:
                files = {
                    'data': ('metadata', json.dumps(file_metadata), 'application/json; charset=UTF-8'),
                    'file': (remote_name, file_data, 'application/octet-stream')
                }
                
                response = requests.post(url, headers=headers, files=files, timeout=60)

            if response.status_code == 200:
                file_info = response.json()
                file_id = file_info.get('id')
                print(f"Backup successful! File: {remote_name}, ID: {file_id}")
                return file_id
            else:
                print(f"Backup failed: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            print(f"Backup failed: {e}")
            return None

    def restore(self, local_file, remote_name, folder_name='backup'):
        """
        Restore a file from Google Drive inside a specified folder - Versión Android.

        :param local_file: Path to save the downloaded file locally.
        :param remote_name: Name of the file on Google Drive.
        :param folder_name: Name of the folder in Google Drive (default: 'backup').
        :return: True if successful, False otherwise.
        """
        try:
            if not self.service:
                print("Authentication failed - cannot restore")
                return False
                
            # Preparar ruta local
            if not os.path.isabs(local_file):
                local_file = os.path.join(self.storage_path, local_file)

            # Get the folder ID
            headers = self._get_headers()
            params = self._get_params()
            
            query = f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder' and trashed=false"
            params['q'] = query
            params['fields'] = 'files(id,name)'
            
            response = requests.get(f"{self.base_url}/files", headers=headers, params=params, timeout=10)
            
            if response.status_code != 200:
                print(f"Error searching folder: {response.status_code}")
                return False
                
            folders = response.json().get('files', [])
            if not folders:
                print(f"No folder named '{folder_name}' found on Google Drive.")
                return False
                
            folder_id = folders[0]['id']

            # Search for the file inside the folder
            query = f"'{folder_id}' in parents and name='{remote_name}' and trashed=false"
            params = self._get_params()
            params['q'] = query
            params['fields'] = 'files(id,name,size)'
            
            response = requests.get(f"{self.base_url}/files", headers=headers, params=params, timeout=10)
            
            if response.status_code != 200:
                print(f"Error searching file: {response.status_code}")
                return False
                
            files = response.json().get('files', [])
            if not files:
                print(f"No file named '{remote_name}' found in folder '{folder_name}'.")
                return False

            # Download the file with progress
            file_id = files[0]['id']
            file_size = files[0].get('size', 0)
            
            # Preparar URL de descarga
            download_url = f"{self.base_url}/files/{file_id}?alt=media"
            
            response = requests.get(download_url, headers=headers, timeout=60, stream=True)
            
            if response.status_code == 200:
                # Crear directorio si no existe
                os.makedirs(os.path.dirname(local_file), exist_ok=True)
                
                # Descargar con progress
                downloaded = 0
                with open(local_file, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                            downloaded += len(chunk)
                            
                            # Mostrar progreso
                            if file_size and int(file_size) > 0:
                                progress = int((downloaded / int(file_size)) * 100)
                                print(f"Download {progress}%.")
                            else:
                                print(f"Downloaded {downloaded} bytes...")
                
                print(f"Restore successful! File saved to: {local_file}")
                return True
            else:
                print(f"Download failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"Restore failed: {e}")
            return False

    def list_files_in_folder(self, folder_name):
        """
        Listar archivos en una carpeta específica.
        
        :param folder_name: Nombre de la carpeta
        :return: Lista de archivos o None si error
        """
        try:
            if not self.service:
                return None
                
            # Buscar carpeta
            headers = self._get_headers()
            params = self._get_params()
            
            query = f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder' and trashed=false"
            params['q'] = query
            params['fields'] = 'files(id,name)'
            
            response = requests.get(f"{self.base_url}/files", headers=headers, params=params, timeout=10)
            
            if response.status_code != 200:
                return None
                
            folders = response.json().get('files', [])
            if not folders:
                return None
                
            folder_id = folders[0]['id']
            
            # Listar archivos en la carpeta
            query = f"'{folder_id}' in parents and trashed=false"
            params = self._get_params()
            params['q'] = query
            params['fields'] = 'files(id,name,size,modifiedTime)'
            params['orderBy'] = 'modifiedTime desc'
            
            response = requests.get(f"{self.base_url}/files", headers=headers, params=params, timeout=10)
            
            if response.status_code == 200:
                return response.json().get('files', [])
            else:
                return None
                
        except Exception as e:
            print(f"Error listing files: {e}")
            return None

def mainDrive():
    """
    Función principal para testing - Mantiene la funcionalidad original.
    
    CONFIGURACIÓN REQUERIDA:
    1. Crear archivo 'credentials.json' con:
       {
         "access_token": "tu_access_token_de_oauth_playground"
       }
    2. Obtener access_token desde: https://developers.google.com/oauthplayground/
       - Scope: https://www.googleapis.com/auth/drive
    """
    # Crear una instancia de la API
    gdrive = GDriveAPI()

    if not gdrive.service:
        print("❌ Authentication failed!")
        print("\n📋 SETUP INSTRUCTIONS:")
        print("1. Go to: https://developers.google.com/oauthplayground/")
        print("2. In 'Step 1', add scope: https://www.googleapis.com/auth/drive")
        print("3. Click 'Authorize APIs' and complete OAuth flow")
        print("4. In 'Step 2', click 'Exchange authorization code for tokens'")
        print("5. Copy the 'Access token'")
        print("6. Create 'credentials.json' file with:")
        print('   {"access_token": "your_access_token_here"}')
        return

    from datetime import datetime

    # Obtener la fecha y hora actual
    fecha_hora_actual = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    # Hacer un backup en la carpeta 'my_backups' (comentado para testing)
    print("🔄 Starting backup...")
    backup_id = gdrive.backup(local_file='pdvDB.sqlite', 
                             remote_name=f'pdvDB_backup_{fecha_hora_actual}.sqlite', 
                             folder_name='Punto de Venta (Respaldos)')
    if backup_id:
        print(f"✅ Backup successful! File ID: {backup_id}")
    else:
        print("❌ Backup failed!")
    
    # Restaurar un archivo desde la carpeta 'my_backups'
    print("\n🔄 Starting restore...")
    restored = gdrive.restore(local_file='pdvDB_restored.sqlite',  
                             remote_name='pdvDB_backup', 
                             folder_name='Punto de Venta (Respaldos)')
    if restored:
        print("✅ Restore successful!")
    else:
        print("❌ Restore failed!")
        
    # Listar archivos en la carpeta (bonus)
    print("\n📁 Files in backup folder:")
    files = gdrive.list_files_in_folder('Punto de Venta (Respaldos)')
    if files:
        for file in files:
            print(f"   - {file['name']} ({file.get('size', 'Unknown')} bytes)")
    else:
        print("   No files found or folder doesn't exist")

if __name__=='__main__':
    mainDrive()