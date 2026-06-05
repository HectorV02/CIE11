import ollama
import csv
import time
import json
#modeloAProbar = "llama3.1:8b"
#archivoSalida = "resultadosLlama3.1_V2.csv"
modeloAProbar = "phi4"
archivoSalida = "resultadosPhi4_V2.csv"
#modeloAProbar = "mistral-small"
#archivoSalida = "resultadosMistralSmall_V2.csv"
#modeloAProbar = "gemma3:27b"
#archivoSalida = "resultadosGemma3_V2.csv"
#modeloAProbar = "qwen3.5:9b"
#archivoSalida = "resultadosQwen3.5_V2.csv"
#modeloAProbar = "gpt-oss:20b"
#archivoSalida = "resultadosGptOss_V2.csv"
archivoEntrada = "datos_cmd_limpio.json"

print("Cargando variables...")
try:
    with open(archivoEntrada, "r", encoding="utf-8") as archivo:
        variables = json.load(archivo)
    print("Variables cargadas exitosamente.")
except Exception as e:
    print(f"Error al leer archivo JSON: {e}")
    exit()

"""
Eres un sistema experto en extracción de información médica y codificación clínica de la CIE-11. Tu tarea es analizar el texto clínico provisto y extraer las entidades diagnósticas, separando la enfermedad principal, los elementos de poscoordinación (divididos en modificadores y enfermedades secundarias), y el contexto demográfico/clínico.

Debes responder ÚNICAMENTE con un objeto JSON válido, sin texto introductorio, sin explicaciones fuera del JSON y sin bloques de código markdown.

### REGLAS DE EXTRACCIÓN:
1. "contexto": Extrae la edad del paciente (en años o meses) y la especialidad médica si se menciona o infiere claramente. Si no aparece, usa null.
2. "diagnostico_principal": El trastorno, enfermedad o síntoma primario que motiva la atención médica.
3. "poscoordinacion": Estructura la poscoordinación en dos subcategorías precisas según la sintaxis de la CIE-11:
   a) "modificadores" (conceptos que usan el conector "&"): Factores que añaden especificidad al diagnóstico principal pero no son diagnósticos independientes (ej. lateralidad, anatomía específica, gravedad, evolución temporal, agentes causales, estadio, síntomas asociados).
   b) "enfermedades_secundarias" (conceptos que usan el conector "/"): Afecciones adicionales, comorbilidades o diagnósticos secundarios que están asociados o se presentan en conjunto con la afección principal.
4. "ruido_clinico": Antecedentes familiares irrelevantes para el episodio actual, síntomas descartados explícitamente ("se descarta...", "negativo para..."), o comentarios administrativos.
5. "explicacion": Breve justificación de cómo se estructuraron los datos.

### EJEMPLO DE ENTRADA:
"Especialidad: Pediatría. Paciente varón de 6 años es traído por fiebre alta y dolor de oído derecho de 48 hrs de evolución secundario a una infección viral de vías respiratorias altas. Otoscopia revela abombamiento y eritema de la membrana timpánica derecha. Diagnóstico: Otitis media aguda supurativa. Se descarta mastoiditis. Sin alergias conocidas."

### EJEMPLO DE SALIDA (JSON):
{
  "contexto": {
    "edad": "6 años",
    "especialidad": "Pediatría"
  },
  "diagnostico_principal": "Otitis media aguda supurativa",
  "poscoordinacion": {
    "modificadores": {
      "lateralidad": "derecho",
      "sintomas_asociados": ["fiebre alta", "dolor de oído"],
      "temporalidad": "aguda"
    },
    "enfermedades_secundarias": [
      "infección viral de vías respiratorias altas"
    ]
  },
  "ruido_clinico": [
    "se descarta mastoiditis",
    "sin alergias conocidas",
    "paciente traído por"
  ],
  "explicacion": "Se establece la otitis como diagnóstico principal. En la poscoordinación, la lateralidad y los síntomas actúan como modificadores (&), mientras que la infección de vías respiratorias altas es una enfermedad secundaria asociada (/). El ruido clínico contiene descartes."
}

### TEXTO CLÍNICO A PROCESAR:
edad del paciente: {edad}
especialidad médica: {especialidad}
diagnóstico clínico: {diagnostico}
"""
#DESPUES PROBAR ESTE OTRO PROMPT, QUE ES MÁS DETALLADO Y EXPLÍCITO EN LA ESTRUCTURA DE LOS DATOS A EXTRAER, PARA VER SI OBTENEMOS MEJORES RESULTADOS:
promtBase = """
Eres un sistema experto en análisis de lenguaje natural médico y arquitecto de datos clínicos para la CIE-11. Tu tarea es analizar el texto clínico provisto, razonar paso a paso su estructura ontológica, y extraer las entidades diagnósticas clasificándolas exactamente según el modelo de poscoordinación de la OMS.

Debes responder ÚNICAMENTE con un objeto JSON válido, sin texto introductorio, sin explicaciones fuera del JSON y sin bloques de código markdown (ni siquiera ```json).

### REGLAS DE EXTRACCIÓN Y RAZONAMIENTO:
1. Cadena de pensamiento oculta: Utiliza el campo "analisis_previo" para pensar en voz alta sobre el caso clínico antes de estructurar los datos. Identifica qué es lo principal, qué es un modificador y qué es una comorbilidad basándote en la gramática clínica.
2. "contexto": Extrae la edad del paciente y la especialidad. Si no se especifican en el texto libre, extrae la información de las variables de entrada.
3. "diagnostico_principal": La afección núcleo que motiva la atención. Debe ser un concepto clínico singular.
4. "poscoordinacion": 
   a) "modificadores" (Eje de los ampersands &): Conceptos dependientes que añaden detalle al diagnóstico principal (lateralidad, gravedad, agudo/crónico, anatomía específica, microorganismos causales, etc.).
   b) "enfermedades_secundarias" (Eje de las barras /): Comorbilidades o diagnósticos independientes asociados. PISTA VITAL: Búscalas explícitamente después de conectores como "con", "secundario a", "debido a", "asociado a", "complicado por", o "y".
5. "ruido_clinico": Aísla y descarta aquí signos vitales normales, antecedentes familiares/personales no relacionados al episodio actual, patologías descartadas explícitamente ("se descarta...", "negativo para...") y lenguaje netamente administrativo.
6. "explicacion": Breve resumen final de la lógica aplicada tras la extracción.

### ESTRUCTURA JSON REQUERIDA (Esquema estricto):
{
  "analisis_previo": "Razonamiento paso a paso: 1) Entender el escenario clínico general... 2) Aislar el diagnóstico principal... 3) Detectar modificadores (tiempo, lugar, gravedad)... 4) Buscar patologías secundarias usando conectores clave...",
  "contexto": {
    "edad": "...",
    "especialidad": "..."
  },
  "diagnostico_principal": "...",
  "poscoordinacion": {
    "modificadores": {
      "lateralidad": "...",
      "temporalidad": "...",
      "gravedad": "...",
      "anatomia_especifica": "...",
      "otros": ["..."]
    },
    "enfermedades_secundarias": ["..."]
  },
  "ruido_clinico": ["..."],
  "explicacion": "..."
}

### TEXTO CLÍNICO A PROCESAR:
Edad del paciente: {edad}
Especialidad médica: {especialidad}
Diagnóstico clínico: {diagnostico}
"""
print("Iniciando pruebas...")
with open(archivoSalida, "w", newline="", encoding="utf-8") as archivoCSV:
    escritor = csv.writer(archivoCSV, delimiter=";")
    escritor.writerow(["diagnostico", "contexto", "elementos_poscoordinacion", "ruido_clinico", "tiempo_respuesta", "explicacion"])
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
                messages = [{"role": "user", "content": promtCompleto}],
                options={
                    'temperature': 0.0, # Anula la creatividad y alucinaciones
                    'num_ctx': 4096     # Opcional: Aumenta la ventana de contexto si el texto es muy largo
                }
            )
            textoRespuesta = respuesta.message.content
            tiempoFin = time.time()
            tiempoTotal = round(tiempoFin - tiempoInicio, 2)
            #print("Respuesta: ", textoRespuesta)
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
            explicacion = datos_json.get("explicacion", "")
            escritor.writerow([
                diagnostico, 
                contexto, 
                post_coord, 
                ruido_clinico, 
                tiempoTotal,
                explicacion
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
    """
    ejemplo = variables[0]
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
        print("Respuesta: ", textoRespuesta)
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
    """
print(f"\n--- Pruebas finalizadas. Resultados guardados en '{archivoSalida}' ---")