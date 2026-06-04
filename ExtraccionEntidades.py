import ollama
import csv
import time
import json
modeloAProbar = "llama3.1:8b"
archivoSalida = "resultadosLlama3.1_V2.csv"
archivoEntrada = "datos_cmd_limpio.json"

print("Cargando variables...")
try:
    with open(archivoEntrada, "r", encoding="utf-8") as archivo:
        variables = json.load(archivo)
    print("Variables cargadas exitosamente.")
except Exception as e:
    print(f"Error al leer archivo JSON: {e}")
    exit()

promtBase = """
Eres un sistema experto en extracción de información médica y codificación clínica de la CIE-11. Tu tarea es analizar el texto clínico provisto y extraer las entidades diagnósticas, separando la enfermedad principal, los elementos de poscoordinación, y el contexto demográfico/clínico.

Debes responder ÚNICAMENTE con un objeto JSON válido, sin texto introductorio, sin explicaciones y sin bloques de código markdown.

### REGLAS DE EXTRACCIÓN:
1. "contexto": Extrae la edad del paciente (en años o meses) y la especialidad médica si se menciona o infiere claramente. Si no aparece, usa null.
2. "diagnostico_principal": El trastorno, enfermedad o síntoma primario que motiva la atención médica.
3. "elementos_poscoordinacion": Factores que modifican o añaden especificidad al diagnóstico principal según los ejes de la CIE-11 (ej. lateralidad, anatomía específica, gravedad, cronicidad, agentes causales, estadio).
4. "ruido_clinico": Antecedentes familiares irrelevantes para el episodio actual, síntomas descartados explícitamente ("se descarta...", "negativo para..."), o comentarios administrativos.

### EJEMPLO DE ENTRADA:
"Especialidad: Pediatría. Paciente varón de 6 años es traído por fiebre alta y dolor de oído derecho de 48 hrs de evolución. Otoscopia revela abombamiento y eritema de la membrana timpánica derecha. Diagnóstico: Otitis media aguda supurativa. Se descarta mastoiditis. Sin alergias conocidas."

### EJEMPLO DE SALIDA (JSON):
{
  "contexto": {
    "edad": "6 años",
    "especialidad": "Pediatría"
  },
  "diagnostico_principal": "Otitis media aguda supurativa",
  "elementos_poscoordinacion": {
    "lateralidad": "derecho",
    "sintomas_asociados": ["fiebre alta", "dolor de oído"],
    "temporalidad": "aguda"
  },
  "ruido_clinico": [
    "se descarta mastoiditis",
    "sin alergias conocidas",
    "paciente traído por"
  ],
  "explicacion": se establece el diagnóstico principal basado en la descripción clínica y los hallazgos otoscópicos, mientras que el ruido clínico se identifica por los antecedentes familiares irrelevantes y los síntomas descartados explícitamente.
}

### TEXTO CLÍNICO A PROCESAR:
edad del paciente: {edad}
especialidad médica: {especialidad}
diagnóstico clínico: {diagnostico}
"""
print("Iniciando pruebas...")
with open(archivoSalida, "w", newline="", encoding="utf-8") as archivoCSV:
    escritor = csv.writer(archivoCSV)
    escritor.writerow(["diagnostico", "contexto", "elementos_poscoordinacion", "ruido_clinico", "tiempo_respuesta"])
    
    for ejemplo in variables:
        diagnostico = ejemplo["text"]
        print(f"Procesando diagnóstico: {diagnostico}")
        promtCompleto = promtBase.replace("{diagnostico}", diagnostico)
        promtCompleto = promtCompleto.replace("{especialidad}", ejemplo["specialty"])
        promtCompleto = promtCompleto.replace("{edad}", str(ejemplo["age"]))
        tiempoInicio = time.time()
        try:
            respuesta = ollama.chat(
                model = modeloAProbar, 
                messages = [{"role": "user", "content": promtCompleto}]
            )
            textoRespuesta = respuesta.message.content
            tiempoFin = time.time()
            tiempoTotal = round(tiempoFin - tiempoInicio, 2)
            
            # Escribimos el resultado en el archivo CSV
            texto_limpio = textoRespuesta.strip()
            if texto_limpio.startswith("```json"):
                texto_limpio = texto_limpio[7:]
            if texto_limpio.startswith("```"):
                texto_limpio = texto_limpio[3:]
            if texto_limpio.endswith("```"):
                texto_limpio = texto_limpio[:-3]
            texto_limpio = texto_limpio.strip()
            datos_json = json.loads(texto_limpio)
            diagnostico = datos_json.get("diagnostico_principal", {})
            post_coord = json.dumps(datos_json.get("elementos_poscoordinacion", []), ensure_ascii=False)
            ruido_clinico = datos_json.get("ruido_clinico", "")
            contexto = datos_json.get("contexto", "")
            escritor.writerow([
                diagnostico, 
                contexto, 
                post_coord, 
                ruido_clinico, 
                tiempoTotal
            ])
            print("Completado. Respuesta obtenida en", tiempoTotal, "segundos.")
        except Exception as e:
            tiempoFin = time.time()
            tiempoTotal = round(tiempoFin - tiempoInicio, 2)
            # Si hay un error, lo guardamos para el registro
            escritor.writerow([
                diagnostico, 
                "Error", 
                "Error", 
                "Error", 
                "Error",
                f"Error al procesar: {e}", 
                tiempoTotal
            ])
            print(f"Error al procesar: {e}")
print(f"\n--- Pruebas finalizadas. Resultados guardados en '{archivoSalida}' ---")