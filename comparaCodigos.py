import json
import csv

# ==========================================
# CONFIGURACIÓN DE ARCHIVOS
# ==========================================
ARCHIVO_JSON_REALES = 'datos_cmd_limpio.json'
ARCHIVO_CSV_GENERADOS = 'codificados/codificadosQwen.csv'
ARCHIVO_REPORTE = 'reporte/reporteQwen.csv'

def cargar_reales(ruta_json):
    """Carga los datos reales desde el archivo JSON."""
    with open(ruta_json, 'r', encoding='utf-8') as f:
        return json.load(f)

def cargar_generados(ruta_csv):
    """Carga los datos generados por la IA y Docker desde el CSV."""
    filas = []
    with open(ruta_csv, 'r', encoding='utf-8') as f:
        lector = csv.DictReader(f, delimiter=';')
        for fila in lector:
            filas.append(fila)
    return filas

def evaluar_coincidencia(codigo_real, codigo_gen_multiple):
    """
    Evalúa el nivel de coincidencia sobre múltiples opciones.
    Devuelve una tupla: (Resultado, Codigo_Que_Coincidio)
    """
    codigo_real = codigo_real.strip().upper()
    
    if codigo_gen_multiple.strip().upper() == "SIN CÓDIGO" or not codigo_gen_multiple:
        return "Fallida", "Ninguno"
        
    # Separar las múltiples opciones usando el delimitador "|"
    opciones_generadas = [opcion.strip().upper() for opcion in codigo_gen_multiple.split('|')]
    
    # 1. Buscar primero si hay ALGUNA coincidencia exacta
    for opcion in opciones_generadas:
        if opcion == codigo_real:
            return "Exacta", opcion
            
    # 2. Si no hay exacta, buscar si hay ALGUNA coincidencia parcial
    for opcion in opciones_generadas:
        # El código generado está contenido dentro del código real (ej. post-coordinación)
        if opcion in codigo_real:
            return "Parcial", opcion
            
    # 3. Si ninguna iteración tuvo éxito, es fallida
    return "Fallida", "Ninguno"

def comparar_datos():
    print("Cargando archivos...")
    try:
        reales = cargar_reales(ARCHIVO_JSON_REALES)
        generados = cargar_generados(ARCHIVO_CSV_GENERADOS)
    except FileNotFoundError as e:
        print(f"Error: No se encontró el archivo. {e}")
        return

    # Verificar que tengan la misma cantidad de filas
    if len(reales) != len(generados):
        print(f"⚠️ Advertencia: El JSON tiene {len(reales)} registros y el CSV tiene {len(generados)}.")
        print("Se compararán hasta donde coincidan las filas.\n")

    resultados = []
    estadisticas = {"Exacta": 0, "Parcial": 0, "Fallida": 0, "Total": 0}

    # Iterar emparejando fila a fila (asumiendo que mantienen el mismo orden)
    for i, (real, gen) in enumerate(zip(reales, generados)):
        texto_real = real.get('text', '')
        codigo_real = real.get('code', '')
        
        texto_gen = gen.get('diagnostico_principal', '')
        codigo_gen_multiple = gen.get('codigo_cie11', 'Sin código')
        
        # Obtenemos la evaluación y cuál fue el código que hizo "match"
        evaluacion, codigo_match = evaluar_coincidencia(codigo_real, codigo_gen_multiple)
        
        estadisticas[evaluacion] += 1
        estadisticas["Total"] += 1
        
        resultados.append({
            'fila': i + 1,
            'texto_original_json': texto_real,
            'texto_extraido_csv': texto_gen,
            'codigo_real_json': codigo_real,
            'opciones_generadas_csv': codigo_gen_multiple,
            'codigo_coincidente': codigo_match, # NUEVA COLUMNA
            'resultado': evaluacion
        })

    # Guardar el reporte
    with open(ARCHIVO_REPORTE, 'w', encoding='utf-8', newline='') as f:
        # Agregamos la nueva columna al reporte
        campos = ['fila', 'texto_original_json', 'texto_extraido_csv', 'codigo_real_json', 'opciones_generadas_csv', 'codigo_coincidente', 'resultado']
        escritor = csv.DictWriter(f, fieldnames=campos, delimiter=';')
        
        escritor.writeheader()
        escritor.writerows(resultados)

    # Imprimir resumen
    print("=========================================")
    print("📊 RESUMEN DE LA COMPARACIÓN (TOP-K ACCURACY)")
    print("=========================================")
    print(f"Total evaluados : {estadisticas['Total']}")
    print(f"✅ Exactas      : {estadisticas['Exacta']} ({(estadisticas['Exacta']/estadisticas['Total'])*100:.2f}%)")
    print(f"⚠️ Parciales    : {estadisticas['Parcial']} ({(estadisticas['Parcial']/estadisticas['Total'])*100:.2f}%)")
    print(f"❌ Fallidas     : {estadisticas['Fallida']} ({(estadisticas['Fallida']/estadisticas['Total'])*100:.2f}%)")
    print("=========================================")
    print(f"Reporte detallado guardado en: {ARCHIVO_REPORTE}")

if __name__ == '__main__':
    comparar_datos()