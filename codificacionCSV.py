import requests
import urllib.parse
import csv
import re
import os
from dotenv import load_dotenv

# ==========================================
# 1. CREDENCIALES
# ==========================================
load_dotenv()
CLIENT_ID = os.getenv('CLIENT_ID')
CLIENT_SECRET = os.getenv('CLIENT_SECRET')
print(CLIENT_ID, CLIENT_SECRET)

# ==========================================
# 2. OBTENER EL TOKEN DE AUTENTICACIÓN
# ==========================================
def obtener_token():
    token_endpoint = 'http://icdaccessmanagement.who.int/connect/token'
    payload = {
        'grant_type': 'client_credentials',
        'scope': 'icdapi_access'
    }
    
    print("Obteniendo token de autenticación de la OMS...")
    response = requests.post(token_endpoint, data=payload, auth=(CLIENT_ID, CLIENT_SECRET))
    
    if response.status_code == 200:
        return response.json()['access_token']
    else:
        raise Exception(f"Error al obtener token: {response.status_code} - {response.text}")

# ==========================================
# 3. BÚSQUEDA EN CONTENEDOR DOCKER LOCAL
# ==========================================
def buscar_codigo_cie11_local(texto_diagnostico, token, puerto_docker="80", num_opciones=3):
    """
    Consulta la API local de la CIE-11 en Docker y devuelve los X códigos y títulos más precisos.
    """
    if texto_diagnostico == "No encontrado" or not texto_diagnostico:
        return "Sin código", "N/A"

    # URL basada en la configuración (2026-01)
    url_base = f"http://localhost:{puerto_docker}/icd/release/11/2026-01/mms/search"
    query = urllib.parse.quote(texto_diagnostico)
    url_completa = f"{url_base}?q={query}"

    # Headers unificados
    headers = {
        'Authorization': f'Bearer {token}',
        'Accept': 'application/json',
        'Accept-Language': 'es',
        'API-Version': 'v2'
    }

    try:
        respuesta = requests.get(url_completa, headers=headers)
        
        if respuesta.status_code == 200:
            datos = respuesta.json()
            
            if 'destinationEntities' in datos and len(datos['destinationEntities']) > 0:
                codigos_extraidos = []
                titulos_extraidos = []
                
                # Iteramos solo hasta el límite definido por num_opciones
                entidades = datos['destinationEntities'][:num_opciones]
                
                for entidad in entidades:
                    codigo = entidad.get('theCode', 'Sin código')
                    
                    # Limpiar etiquetas HTML
                    titulo_bruto = entidad.get('title', '')
                    titulo_limpio = re.sub(r'<[^>]+>', '', titulo_bruto)
                    
                    codigos_extraidos.append(codigo)
                    titulos_extraidos.append(titulo_limpio)
                
                # Unimos las listas con " | " para que queden legibles en una sola celda del CSV
                string_codigos = " | ".join(codigos_extraidos)
                string_titulos = " | ".join(titulos_extraidos)
                
                return string_codigos, string_titulos
            else:
                return "No hubo coincidencias", "N/A"
        else:
            return f"Error API: {respuesta.status_code}", "N/A"
            
    except requests.exceptions.ConnectionError:
        return "Error de conexión local", "N/A"
    except Exception as e:
        return f"Error inesperado", str(e)

# ==========================================
# 4. PROCESAMIENTO DEL ARCHIVO CSV
# ==========================================
def procesar_csv(archivo_entrada, archivo_salida):
    try:
        # Obtenemos el token una sola vez para todas las peticiones
        token = obtener_token()
    except Exception as e:
        print(f"Error fatal de autenticación: {e}")
        return

    print(f"\nIniciando lectura de {archivo_entrada}...\n")

    # Abrimos el CSV de lectura y creamos uno nuevo para la escritura
    with open(archivo_entrada, mode='r', encoding='utf-8') as infile, \
         open(archivo_salida, mode='w', encoding='utf-8', newline='') as outfile:
        
        # El CSV de entrada parece utilizar punto y coma (;) como delimitador
        lector = csv.DictReader(infile, delimiter=';')
        
        # Obtenemos los nombres de las columnas originales y agregamos las nuevas
        nombres_columnas = lector.fieldnames
        if not nombres_columnas:
            print("El archivo CSV está vacío o tiene un formato incorrecto.")
            return
            
        nombres_columnas_nuevas = nombres_columnas + ['codigo_cie11', 'titulo_cie11']
        
        escritor = csv.DictWriter(outfile, fieldnames=nombres_columnas_nuevas, delimiter=';')
        escritor.writeheader()
        
        # Procesamos fila por fila
        for index, fila in enumerate(lector, start=1):
            # Extraemos el texto a codificar de la columna correspondiente
            diagnostico = fila.get('diagnostico_principal', '').strip()
            
            print(f"[{index}] Mapeando: '{diagnostico}'...")
            
            codigo, titulo = buscar_codigo_cie11_local(diagnostico, token)
            
            # Guardamos los resultados en la fila
            fila['codigo_cie11'] = codigo
            fila['titulo_cie11'] = titulo
            
            # Escribimos la fila enriquecida en el nuevo archivo
            escritor.writerow(fila)
            
    print(f"\n✅ Procesamiento completado. Archivo generado: {archivo_salida}")

# ==========================================
# EJECUCIÓN DEL SCRIPT
# ==========================================
if __name__ == '__main__':
    # Nombres de tus archivos
    ARCHIVO_ENTRADA = 'resultados/resultadosQwen.csv'
    ARCHIVO_SALIDA = 'codificados/codificadosQwen.csv'
    
    procesar_csv(ARCHIVO_ENTRADA, ARCHIVO_SALIDA)