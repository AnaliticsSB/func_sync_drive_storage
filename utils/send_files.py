import os
import io
import re
import gspread
import requests
import logging
import json
from google.oauth2.service_account import Credentials
from google.oauth2 import service_account
from google.cloud import secretmanager
from google.cloud import storage
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

def get_credentials():

    client = secretmanager.SecretManagerServiceClient()
    auth_creds = 'projects/911414108629/secrets/gcp_sb-xops-stage/versions/latest'
    response = client.access_secret_version(name=auth_creds).payload.data.decode("UTF-8")
    
    creds_dict = json.loads(response)

    return creds_dict

def initialize_service_drive():
    client = secretmanager.SecretManagerServiceClient()
    secrets = 'projects/911414108629/secrets/gcp_sb-xops-stage/versions/latest'
    response = client.access_secret_version(name=secrets).payload.data.decode("UTF-8")
    client_secret = json.loads(response)

    SCOPES = [
        'https://www.googleapis.com/auth/drive'
    ]

    credentials = Credentials.from_service_account_info(
        client_secret, scopes=SCOPES
    )

    # Conéctate a google sheets:
    gc = gspread.authorize(credentials)

    # Conéctate al servicio de Google Drive
    service = build('drive', 'v3', credentials=credentials)
    
    return service, gc

def download_file_from_drive(drive_url, service):
    # Extraer file ID
    file_id = drive_url.split("/d/")[1].split("/")[0]
    
    # Obtener metadatos para extraer el nombre
    request = service.files().get_media(fileId=file_id)
    file = io.BytesIO()
    downloader = MediaIoBaseDownload(file, request)
    done = False
    
    while done is False:
        status, done = downloader.next_chunk()

    return file.getvalue()

def sync_drive_gcp(project, gcs_bucket, folder, sheet_id, sheet_name):
    """
    Endpoint principal que inicia el proceso de subida de PDFs.
    Se activa con una petición POST vacía.
    """
    PROJECT = project
    BUCKET_NAME = gcs_bucket
    FOLDER = folder
    SHEET_ID = sheet_id
    SHEET_NAME = sheet_name
    
    if not all([PROJECT, BUCKET_NAME, FOLDER, SHEET_ID, SHEET_NAME]):
        return jsonify({"error": "Faltan los parámetros 'project', 'gcs_bucket', 'folder', 'sheet_id', 'sheet_name'."}), 400

    uploaded_files = []
    failed_files = []
    
    service, gc = initialize_service_drive()
    
    # Conectarse a google cloud storage
    cred = get_credentials()
    credentials = service_account.Credentials.from_service_account_info(cred)
    storage_client = storage.Client(credentials= credentials, project = PROJECT)
    
    # Abrir el Google Sheet y la hoja específica
    spreadsheet = gc.open_by_key(SHEET_ID)
    worksheet = spreadsheet.worksheet(SHEET_NAME)
    urls = worksheet.col_values(15)[1:]
    file_names = worksheet.col_values(16)[1:]
    
    if not urls:
      return "No se encontraron URLs en la columna especificada.", 200
    
    print(f"Se encontraron {len(urls)} URLs para procesar.")
    
    
    # Iterar sobre cada URL
    for i in range(0, len(urls)):
      url = urls[i]
      filename = file_names[i]
    
      if not url.startswith('http'):
          print(f"Omitiendo valor no válido: {url}")
          continue
    
    print(f"Procesando: {url}")

    # Descargar el contenido del PDF en memoria
    file_bytes = download_file_from_drive(url, service) 

    # Subir el contenido al bucket de GCS
    bucket = storage_client.bucket(BUCKET_NAME)
    blob = bucket.blob(FOLDER + filename)
    
    # Definir el tipo de contenido para que se visualice correctamente
    blob.upload_from_string(
        file_bytes,
        content_type='application/pdf'
    )

    print(f"Éxito: '{filename}' subido a '{BUCKET_NAME}'.")
    uploaded_files.append(filename)

    summary = f"Proceso completado. Subidos: {len(uploaded_files)}, Fallidos: {len(failed_files)}."
    print(summary)
    return summary, 200
