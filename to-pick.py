#!/usr/bin/env python3
"""
Script para migrar credenciales de Google desde .pickle a .json
Compatible con Android/Kivy
"""

import os
import pickle
import json
from datetime import datetime, timedelta

def migrate_pickle_to_json(pickle_file='token.pickle', json_file='credentials.json'):
    """
    Migrar credenciales desde archivo .pickle a .json
    
    :param pickle_file: Archivo pickle original
    :param json_file: Archivo JSON de salida
    :return: True si exitoso, False si error
    """
    try:
        print(f"🔄 Reading pickle file: {pickle_file}")
        
        # Leer archivo pickle
        if not os.path.exists(pickle_file):
            print(f"❌ Pickle file not found: {pickle_file}")
            return False
            
        with open(pickle_file, 'rb') as token:
            creds = pickle.load(token)
        
        print("✅ Pickle file loaded successfully")
        
        # Extraer información del objeto Credentials
        credentials_data = {}
        
        # Access token (obligatorio)
        if hasattr(creds, 'token') and creds.token:
            credentials_data['access_token'] = creds.token
            print(f"✅ Access token found: {creds.token[:20]}...")
        else:
            print("❌ No access token found in pickle file")
            return False
        
        # Refresh token (para renovar automáticamente)
        if hasattr(creds, 'refresh_token') and creds.refresh_token:
            credentials_data['refresh_token'] = creds.refresh_token
            print(f"✅ Refresh token found: {creds.refresh_token[:20]}...")
        
        # Client ID y Client Secret (para refresh)
        if hasattr(creds, 'client_id') and creds.client_id:
            credentials_data['client_id'] = creds.client_id
            print(f"✅ Client ID found: {creds.client_id}")
            
        if hasattr(creds, 'client_secret') and creds.client_secret:
            credentials_data['client_secret'] = creds.client_secret
            print(f"✅ Client secret found: {creds.client_secret[:10]}...")
        
        # Token URI
        if hasattr(creds, 'token_uri') and creds.token_uri:
            credentials_data['token_uri'] = creds.token_uri
        else:
            # Default token URI
            credentials_data['token_uri'] = 'https://oauth2.googleapis.com/token'
        
        # Scopes
        if hasattr(creds, 'scopes') and creds.scopes:
            credentials_data['scopes'] = list(creds.scopes)
        else:
            credentials_data['scopes'] = ['https://www.googleapis.com/auth/drive']
        
        # Información de expiración
        if hasattr(creds, 'expiry') and creds.expiry:
            credentials_data['expiry'] = creds.expiry.isoformat()
            print(f"✅ Token expires: {creds.expiry}")
            
            # Verificar si el token está expirado
            if creds.expiry < datetime.now(creds.expiry.tzinfo):
                print("⚠️  WARNING: Token is expired - you may need to refresh it")
        
        # Metadata adicional
        credentials_data['migrated_from_pickle'] = True
        credentials_data['migration_date'] = datetime.now().isoformat()
        credentials_data['type'] = 'authorized_user'
        
        # Guardar como JSON
        with open(json_file, 'w') as f:
            json.dump(credentials_data, f, indent=2)
        
        print(f"✅ Migration successful!")
        print(f"📁 Credentials saved to: {json_file}")
        
        # Mostrar resumen
        print("\n📋 MIGRATION SUMMARY:")
        print(f"   - Access token: {'✅' if 'access_token' in credentials_data else '❌'}")
        print(f"   - Refresh token: {'✅' if 'refresh_token' in credentials_data else '❌'}")
        print(f"   - Client credentials: {'✅' if 'client_id' in credentials_data else '❌'}")
        
        if 'refresh_token' not in credentials_data:
            print("\n⚠️  WARNING: No refresh token found!")
            print("   The access token will expire and cannot be automatically renewed.")
            print("   Consider getting a new token with refresh capability.")
        
        return True
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        return False

def test_credentials(json_file='credentials.json'):
    """
    Test de las credenciales migradas
    
    :param json_file: Archivo JSON con credenciales
    :return: True si válido, False si no
    """
    try:
        import requests
        
        print(f"\n🧪 Testing credentials from: {json_file}")
        
        with open(json_file, 'r') as f:
            creds = json.load(f)
        
        if 'access_token' not in creds:
            print("❌ No access token found in JSON file")
            return False
        
        # Test con Google Drive API
        headers = {'Authorization': f'Bearer {creds["access_token"]}'}
        response = requests.get('https://www.googleapis.com/drive/v3/about?fields=user', 
                              headers=headers, timeout=10)
        
        if response.status_code == 200:
            user_info = response.json()
            print(f"✅ Credentials valid!")
            if 'user' in user_info:
                print(f"   Logged in as: {user_info['user'].get('emailAddress', 'Unknown')}")
            return True
        elif response.status_code == 401:
            print("❌ Token expired or invalid")
            
            # Intentar refresh si es posible
            if 'refresh_token' in creds:
                print("🔄 Attempting to refresh token...")
                return refresh_token(json_file)
            else:
                print("   No refresh token available - need new credentials")
                return False
        else:
            print(f"❌ API error: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def refresh_token(json_file='credentials.json'):
    """
    Renovar access token usando refresh token
    
    :param json_file: Archivo JSON con credenciales
    :return: True si exitoso, False si no
    """
    try:
        import requests
        
        with open(json_file, 'r') as f:
            creds = json.load(f)
        
        if 'refresh_token' not in creds:
            print("❌ No refresh token available")
            return False
        
        # Datos para el refresh
        data = {
            'client_id': creds.get('client_id'),
            'client_secret': creds.get('client_secret'),
            'refresh_token': creds['refresh_token'],
            'grant_type': 'refresh_token'
        }
        
        # Remover valores None
        data = {k: v for k, v in data.items() if v is not None}
        
        if not data.get('client_id') or not data.get('client_secret'):
            print("❌ Missing client_id or client_secret for refresh")
            return False
        
        token_uri = creds.get('token_uri', 'https://oauth2.googleapis.com/token')
        response = requests.post(token_uri, data=data, timeout=10)
        
        if response.status_code == 200:
            token_data = response.json()
            
            # Actualizar access token
            creds['access_token'] = token_data['access_token']
            
            # Calcular nueva expiración
            expires_in = token_data.get('expires_in', 3600)  # Default 1 hour
            expiry = datetime.now() + timedelta(seconds=expires_in)
            creds['expiry'] = expiry.isoformat()
            
            # Guardar credenciales actualizadas
            with open(json_file, 'w') as f:
                json.dump(creds, f, indent=2)
            
            print("✅ Token refreshed successfully!")
            return True
        else:
            print(f"❌ Refresh failed: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Refresh error: {e}")
        return False

def main():
    """
    Función principal de migración
    """
    print("🔄 GOOGLE DRIVE CREDENTIALS MIGRATOR")
    print("=" * 50)
    
    # Archivos por defecto
    pickle_file = 'token.pickle'
    json_file = 'credentials.json'
    
    # Verificar si ya existe el JSON
    if os.path.exists(json_file):
        response = input(f"📁 {json_file} already exists. Overwrite? (y/N): ")
        if response.lower() != 'y':
            print("Migration cancelled.")
            return
    
    # Verificar pickle file
    if not os.path.exists(pickle_file):
        custom_pickle = input(f"📁 {pickle_file} not found. Enter pickle file path: ")
        if custom_pickle.strip():
            pickle_file = custom_pickle.strip()
        else:
            print("No pickle file specified. Exiting.")
            return
    
    # Realizar migración
    success = migrate_pickle_to_json(pickle_file, json_file)
    
    if success:
        # Test de las credenciales
        print("\n" + "=" * 50)
        test_success = test_credentials(json_file)
        
        if test_success:
            print("\n🎉 MIGRATION COMPLETE!")
            print(f"✅ Your credentials are ready to use in: {json_file}")
            print("\n📋 NEXT STEPS:")
            print("1. Copy credentials.json to your Android project folder")
            print("2. Update your buildozer.spec:")
            print("   requirements = python3,kivy,requests,certifi")
            print("3. Deploy to Android!")
        else:
            print("\n⚠️  Migration completed but credentials need attention")
            print("Consider getting fresh credentials if refresh failed")
    else:
        print("\n❌ Migration failed - check the error messages above")

if __name__ == '__main__':
    main()