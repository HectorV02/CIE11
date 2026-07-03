import csv

# ==========================================
# CONFIGURACIÓN DE ARCHIVOS
# ==========================================
ARCHIVO_CSV_GENERADOS = 'OpenRouter/codificadosV2/codificadosZ.csv'
ARCHIVO_REPORTE = 'OpenRouter/reportesV2/reporteZ.csv'
#ARCHIVO_CSV_GENERADOS = 'Locales/codificadosV2/codificadosQwen.csv'
#ARCHIVO_REPORTE = 'Locales/reportesV2/reporteQwen.csv'

def evaluar_coincidencia(codigo_real, codigo_gen_multiple):
    """
    Evalúa el nivel de coincidencia sobre múltiples opciones.
    Devuelve una tupla: (Resultado, Codigo_Que_Coincidio)
    """
    codigo_real = codigo_real.strip().upper()
    
    if codigo_gen_multiple.strip().upper() == "SIN CÓDIGO" or not codigo_gen_multiple:
        return "Fallida", "Ninguno"
        
    opciones_generadas = [opcion.strip().upper() for opcion in codigo_gen_multiple.split('|')]
    
    for opcion in opciones_generadas:
        if opcion == codigo_real:
            return "Exacta", opcion
            
    for opcion in opciones_generadas:
        if opcion in codigo_real:
            return "Parcial", opcion
            
    return "Fallida", "Ninguno"

def comparar_datos():
    print("Cargando archivo unificado...")
    resultados = []
    estadisticas = {"Exacta": 0, "Parcial": 0, "Fallida": 0, "Total": 0}

    try:
        with open(ARCHIVO_CSV_GENERADOS, 'r', encoding='latin-1') as f: # Usamos utf-8-sig por si viene de Excel
            lector = csv.DictReader(f, delimiter=';')
            
            for fila in lector:
                # 1. Extraemos los datos reales que pusiste a mano
                id_fila = fila.get('ID', 'N/A')
                texto_real = fila.get('texto_original', '')
                codigo_real = fila.get('codigo_real', '')
                
                # 2. Extraemos los datos generados por el LLM y la OMS
                texto_gen = fila.get('diagnostico_principal', '')
                codigo_gen_multiple = fila.get('codigo_cie11', 'Sin código')
                
                # 3. Evaluamos (Misma lógica robusta que ya tenías)
                evaluacion, codigo_match = evaluar_coincidencia(codigo_real, codigo_gen_multiple)
                
                estadisticas[evaluacion] += 1
                estadisticas["Total"] += 1
                
                resultados.append({
                    'ID': id_fila,
                    'texto_original': texto_real,
                    'texto_extraido_csv': texto_gen,
                    'codigo_real': codigo_real,
                    'opciones_generadas_csv': codigo_gen_multiple,
                    'codigo_coincidente': codigo_match,
                    'resultado': evaluacion
                })
    except FileNotFoundError:
        print(f"Error: No se encontró el archivo {ARCHIVO_CSV_GENERADOS}")
        return
    except KeyError as e:
        print(f"Error: Falta una columna en el CSV. Asegúrate de que se llame exactamente: {e}")
        return

    # Guardar el reporte
    with open(ARCHIVO_REPORTE, 'w', encoding='latin-1', newline='') as f:
        campos = ['ID', 'texto_original', 'texto_extraido_csv', 'codigo_real', 'opciones_generadas_csv', 'codigo_coincidente', 'resultado']
        escritor = csv.DictWriter(f, fieldnames=campos, delimiter=';')
        
        escritor.writeheader()
        escritor.writerows(resultados)

    # Imprimir resumen
    print("=========================================")
    print("📊 RESUMEN DE LA COMPARACIÓN (TOP-K ACCURACY)")
    print("=========================================")
    print(f"Total evaluados : {estadisticas['Total']}")
    if estadisticas['Total'] > 0:
        print(f"✅ Exactas      : {estadisticas['Exacta']} ({(estadisticas['Exacta']/estadisticas['Total'])*100:.2f}%)")
        print(f"⚠️ Parciales    : {estadisticas['Parcial']} ({(estadisticas['Parcial']/estadisticas['Total'])*100:.2f}%)")
        print(f"❌ Fallidas     : {estadisticas['Fallida']} ({(estadisticas['Fallida']/estadisticas['Total'])*100:.2f}%)")
    print("=========================================")
    print(f"Reporte detallado guardado en: {ARCHIVO_REPORTE}")

if __name__ == '__main__':
    comparar_datos()