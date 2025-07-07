import json
import sqlalchemy
import pandas as pd
import datetime as dt

from utils.connect_sql import getEngine

def request_postgres(input_query):

  # Crear el motor de SQLAlchemy
  engine = getEngine()
  
  with engine.connect() as connection:

    results = connection.execute(sqlalchemy.text(input_query))

    data = pd.DataFrame(results.fetchall())
    
    return data

def consulta_producto_759(tipoDocumento, numeroDocumento, fecha):

  # Se obtienen los atributos de parameters:
  tipo_documento = str(tipoDocumento)
  numero_documento = int(numeroDocumento)
  fecha = str(fecha)

  # Se define el query a realizar:
  query = """
          SELECT *
          FROM "api_backend"."759_productos_polizas"
          WHERE "numeroDocumento" = {}
              AND "tipoDocumento" = '{}'
              AND to_date('{}' , 'DD/MM/YYYY') BETWEEN to_date("fechaInicio" , 'DD/MM/YYYY') AND to_date("fechaFin" , 'DD/MM/YYYY')
          """.format(numero_documento, tipo_documento, fecha)
  
  # Se obtiene el resultado del query:
  response = request_postgres(query)
  
  response = json.loads(response.to_json(orient='records', date_format='iso'))

  for i in range(0, len(response)):
    response[i]["coberturas"] = json.loads(response[i]["coberturas"])
  
  return response
