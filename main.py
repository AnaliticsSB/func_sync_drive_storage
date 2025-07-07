import sys 
sys.path.append('.')

#* Librerías para el API
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from fastapi.responses import RedirectResponse
import os

#* Librerías propias para el funcionamiento del API
from utils.request_postgres import consulta_polizas_vigentes_tron


#* Definición del tipo de input
class TextInput(BaseModel): #! Cambiar esto
    tipoDocumento: str = Field(..., example="CC", description="Se espera el tipo de documento del usuario/cliente a consultar")
    numeroDocumento: str = Field(..., example="123456789", description="Se espera el número de documento del usuario/cliente a consultar")
    compania: str = Field(..., example="2", description="Se espera el código de la compania que emitio la póliza")
    seccion: str = Field(..., example="1", description="Se espera el cógido de ramo emisión de la póliza")
    poliza: str = Field(..., example="0123456789123", description="Se espera número de la póliza (con altura) a consultar")
    
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
descripcion_path = 'API que retorna la información del último endoso de las pólizas vigentes' #! Cambiar esto
summary_path = 'EndPoint que realiza una consulta a la base productiva PostgresSQL para la API Pólizas Vigentes Tronador' #! Cambiar esto
endpoint_end = '/api_tron_polizas_vigentes' #! Cambiar esto
@app.post(endpoint_end, summary = summary_path, description = descripcion_path)
async def ejemplo(input: TextInput):
    response = consulta_polizas_vigentes_tron(tipoDocumento = input.tipoDocumento, numeroDocumento = input.numeroDocumento, compania = input.compania, seccion = input.seccion, poliza = input.poliza) #! Cambiar esto
    return response

@app.get("/", response_class=RedirectResponse)
async def redirect_to_docs():
    return "/docs"

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=int(puerto))
