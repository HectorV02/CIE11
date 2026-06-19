import requests
import json
import os
from dotenv import load_dotenv

# ==========================================
# 1. TUS CREDENCIALES
# ==========================================
load_dotenv()
CLIENT_ID = os.getenv('CLIENT_ID')
CLIENT_SECRET = os.getenv('CLIENT_SECRET')

# ==========================================
# 2. OBTENER EL TOKEN DE AUTENTICACIÓN
# ==========================================
def obtener_token():
    token_endpoint = 'http://icdaccessmanagement.who.int/connect/token'
    payload = {
        'grant_type': 'client_credentials',
        'scope': 'icdapi_access'
    }
    
    print("Obteniendo token de la OMS...")
    # La API de la OMS usa Basic Auth para entregar el token
    response = requests.post(token_endpoint, data=payload, auth=(CLIENT_ID, CLIENT_SECRET))
    
    if response.status_code == 200:
        return response.json()['access_token']
    else:
        raise Exception(f"Error al obtener token: {response.status_code} - {response.text}")

# ==========================================
# 3. BUSCAR Y EXTRAER DATOS EN ESPAÑOL
# ==========================================
def buscar_en_cie11(termino_busqueda, token):
    # Endpoint de búsqueda en la versión MMS (la versión clínica/estadística estándar)
    # mms = Mortality and Morbidity Statistics
    # icf = Clasificación Internacional del Funcionamiento, de la Discapacidad y de la Salud
    search_url = f'http://localhost/icd/release/11/2026-01/mms/search?q={termino_busqueda}'
    
    # ¡ESTOS HEADERS SON LA CLAVE!
    headers = {
        'Authorization': f'Bearer {token}',
        'Accept': 'application/json',
        'Accept-Language': 'es', # <--- Esto fuerza que los títulos y sinónimos vengan en español
        'API-Version': 'v2'
    }
        
    print(f"Buscando: '{termino_busqueda}'...")
    response = requests.get(search_url, headers=headers)
    
    if response.status_code == 200:
        resultados = response.json()
        
        # Procesamos los resultados para extraer lo que le sirve a tu RAG
        entidades_procesadas = []
        for destino in resultados.get('destinationEntities', []):
            codigo = destino.get('theCode', 'Sin Código')
            titulo = destino.get('title', '').replace('<em>', '').replace('</em>', '') # Limpiar HTML
            
            # Extraer sinónimos (matching terms)
            sinonimos = []
            for matching_term in destino.get('matchingPVs', []):
                term = matching_term.get('label', '').replace('<em>', '').replace('</em>', '')
                if term and term not in sinonimos:
                    sinonimos.append(term)
            
            entidades_procesadas.append({
                'codigo': codigo,
                'titulo_oficial': titulo,
                'sinonimos': sinonimos
            })
            
        return entidades_procesadas
    else:
        print(f"Error en la búsqueda: {response.status_code}")
        return []

# ==========================================
# EJECUCIÓN DEL FLUJO
# ==========================================
if __name__ == "__main__":
    lista = []
    try:
        # 1. Autenticarse
        mi_token = obtener_token()
        
        # 2. Hacer una prueba buscando "Colico renal"
        search_url = f'http://localhost/icd/release/11/2026-01/mms/474718032'
        #'child': ['http://localhost/icd/release/11/2026-01/mms/1435254666', 'http://localhost/icd/release/11/2026-01/mms/1630407678', 'http://localhost/icd/release/11/2026-01/mms/1766440644', 'http://localhost/icd/release/11/2026-01/mms/1954798891', 'http://localhost/icd/release/11/2026-01/mms/21500692', 'http://localhost/icd/release/11/2026-01/mms/334423054', 'http://localhost/icd/release/11/2026-01/mms/274880002', 'http://localhost/icd/release/11/2026-01/mms/1296093776', 'http://localhost/icd/release/11/2026-01/mms/868865918', 'http://localhost/icd/release/11/2026-01/mms/1218729044', 'http://localhost/icd/release/11/2026-01/mms/426429380', 'http://localhost/icd/release/11/2026-01/mms/197934298', 'http://localhost/icd/release/11/2026-01/mms/1256772020', 'http://localhost/icd/release/11/2026-01/mms/1639304259', 'http://localhost/icd/release/11/2026-01/mms/1473673350', 'http://localhost/icd/release/11/2026-01/mms/30659757', 'http://localhost/icd/release/11/2026-01/mms/577470983', 'http://localhost/icd/release/11/2026-01/mms/714000734', 'http://localhost/icd/release/11/2026-01/mms/1306203631', 'http://localhost/icd/release/11/2026-01/mms/223744320', 'http://localhost/icd/release/11/2026-01/mms/1843895818', 'http://localhost/icd/release/11/2026-01/mms/435227771', 'http://localhost/icd/release/11/2026-01/mms/850137482', 'http://localhost/icd/release/11/2026-01/mms/1249056269', 'http://localhost/icd/release/11/2026-01/mms/1596590595', 'http://localhost/icd/release/11/2026-01/mms/718687701', 'http://localhost/icd/release/11/2026-01/mms/231358748', 'http://localhost/icd/release/11/2026-01/mms/979408586']
        
        #search_url = f'http://localhost/icd/release/11/2026-01/icf'
        #'child': ['http://localhost/icd/release/11/2026-01/icf/619527855', 'http://localhost/icd/release/11/2026-01/icf/423829389']
    
        # ¡ESTOS HEADERS SON LA CLAVE!
        headers = {
            'Authorization': f'Bearer {mi_token}',
            'Accept': 'application/json',
            'Accept-Language': 'es', # <--- Esto fuerza que los títulos y sinónimos vengan en español
            'API-Version': 'v2'
        }
        response = requests.get(search_url, headers=headers)
        if response.status_code == 200:
            print("Búsqueda exitosa. Procesando resultados...")
            resultados = response.json()
            print(resultados)
            lista.append(resultados)
            print(lista)
            nombre_archivo = 'muestra2.json'
            with open(nombre_archivo, 'w', encoding='utf-8') as archivo:
            # ensure_ascii=False permite que las tildes y ñ se guarden correctamente
            # indent=4 le da el formato bonito con saltos de línea
                json.dump(lista, archivo, ensure_ascii=False, indent=4)
            """
            resultados = response.json()
            resultados = resultados.get('child', []) 
            for child in resultados:
                child = child.replace('http://id.who.int', 'http://localhost')
                r = requests.get(child, headers=headers)
                if r.status_code == 200:
                    lista.append(r.json())
                    #print(r.json())
                else:
                    print(f"Error al obtener detalles de {child}: {r.status_code}")
            print("Resultados obtenidos correctamente.")
            print(resultados)
            nombre_archivo = 'muestra.json'
            with open(nombre_archivo, 'w', encoding='utf-8') as archivo:
            # ensure_ascii=False permite que las tildes y ñ se guarden correctamente
            # indent=4 le da el formato bonito con saltos de línea
                json.dump(lista, archivo, ensure_ascii=False, indent=4)
            """
        else:
            print(f"Error en la búsqueda: {response.status_code}")
        """
        resultados = buscar_en_cie11("colico renal", mi_token)
        
        # 3. Imprimir los resultados listos para tu base vectorial
        print("\n--- RESULTADOS PARA EL RAG ---")
        for idx, item in enumerate(resultados[:3]): # Mostramos solo los 3 primeros
            print(f"\nOpción {idx + 1}:")
            print(f"Código CIE-11: {item['codigo']}")
            print(f"Título:        {item['titulo_oficial']}")
            print(f"Sinónimos:     {', '.join(item['sinonimos'])}")
        """
            
    except Exception as e:
        print(e)
