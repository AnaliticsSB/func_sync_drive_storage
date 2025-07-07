import sys 
sys.path.append('.')

#* Librerías para el API
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from fastapi.responses import RedirectResponse
import os

#* Librerías propias para el funcionamiento del API
from utils.send_files import sync_drive_gcp


#* Definición del tipo de input
class TextInput(BaseModel): #! Cambiar esto
    project: str = Field(..., example="id-proyecto", description="Se espera el nombre del proyecto de GCP")
    gcs_bucket: str = Field(..., example="name-bucket", description="Se espera el nombre del bucket de google cloud storage")
    folder: str = Field(..., example="name-folder", description="Se espera el nombre del folder")
    sheet_id: str = Field(..., example="1fgrgr5g75a7fr5gr5", description="Se espera el id del sheets")
    sheet_name: str = Field(..., example="nombre_hoja", description="Se espera el nombre de la hoja del sheets")
    
# Parametros básicos y clases
app = FastAPI()
puerto = os.environ.get("PORT", 8080)

# Configuración de CORS
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

#* Definición de un endpoint
descripcion_path = 'API que sincroniza archivos de un drive listados en un sheets aun bucket de GCP' #! Cambiar esto
summary_path = 'EndPoint que realiza el envio de archivos de un drive a un bucket de gcp' #! Cambiar esto
endpoint_end = '/sync_files_drive_gcp' #! Cambiar esto
@app.post(endpoint_end, summary = summary_path, description = descripcion_path)
async def ejemplo(input: TextInput):
    response = sync_drive_gcp(project = input.project, gcs_bucket = input.gcs_bucket, folder = input.folder, sheet_id = input.sheet_id, sheet_name = input.sheet_name) #! Cambiar esto
    return response

@app.get("/", response_class=RedirectResponse)
async def redirect_to_docs():
    return "/docs"

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=int(puerto))
