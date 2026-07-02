import ollama
import csv
import time
import json
import re
import os
from dotenv import load_dotenv
import requests
# Modelos que no me dieron
#modeloAProbar = "llama3.1:8b"
#archivoSalida = "resultadosLlama3.1_V2_P2.csv"
#modeloAProbar = "phi4"
#archivoSalida = "resultadosPhi4_V2.csv"
#modeloAProbar = "mistral-small"
#archivoSalida = "resultadosMistralSmall_V2.csv"
#modeloAProbar = "gemma3:27b"
#archivoSalida = "resultadosGemma3_V2.csv"
#modeloAProbar = "qwen3.5:9b"
#archivoSalida = "resultadosQwen3.5_V2.csv"
#modeloAProbar = "gpt-oss:20b"
#archivoSalida = "resultadosGptOss_V2.csv"

# Modelos que si me dieron
#modeloAProbar = "deepseek-r1:7b"
#archivoSalida = "resultadosDeepSeek.csv"
#modeloAProbar = "qwen2.5:7b"
#archivoSalida = "resultadosQwen.csv"
#modeloAProbar = "mistral"
#archivoSalida = "resultadosMistral.csv"
#modeloAProbar = "gemma3:4b"
#archivoSalida = "resultadosGemma.csv"
#modeloAProbar = "phi3.5"
#archivoSalida = "resultadosPhi.csv"
#modeloAProbar = "llama3.2:3b"
#archivoSalida = "resultadosLlama.csv"

# Modelos medicos
#modeloAProbar = "medgemma1.5"
#archivoSalida = "resultadosMedGemma.csv"
#modeloAProbar = "meditron"
#archivoSalida = "resultadosMeditron.csv"
#modeloAProbar = "medllama2"
#archivoSalida = "resultadosMedLlama.csv"

#Locales en Open Router (free)
#modeloAProbar = "qwen/qwen3-next-80b-a3b-instruct:free" -> Rate Limit
#archivoSalida = "openRouterQwen.csv"
#modeloAProbar = "qwen/qwen3-coder:free" -> Rate limit
#archivoSalida = "openRouterQwen2.csv"
#modeloAProbar = "cognitivecomputations/dolphin-mistral-24b-venice-edition:free" -> Rate Limit
#archivoSalida = "openRouterMistral.csv"
#modeloAProbar = "google/gemma-4-31b-it:free"
#archivoSalida = "openRouterGemma.csv"
#modeloAProbar = "google/gemma-4-26b-a4b-it:free"
#archivoSalida = "openRouterGemma2.csv"
#modeloAProbar = "meta-llama/llama-3.3-70b-instruct:free" -> Rate Limit
#archivoSalida = "openRouterLlama.csv"
#modeloAProbar = "meta-llama/llama-3.2-3b-instruct:free" -> Rate Limit
#archivoSalida = "openRouterLlama2.csv"

#Top de Open Router (free)
#modeloAProbar = "openrouter/owl-alpha"
#archivoSalida = "openRouterOWL.csv"
#modeloAProbar = "openai/gpt-oss-120b:free"
#archivoSalida = "openRouterGPT.csv"
#modeloAProbar = "nvidia/nemotron-3-ultra-550b-a55b:free"
#archivoSalida = "openRouteNvidia.csv"
#modeloAProbar = "nvidia/nemotron-3-super-120b-a12b:free"
#archivoSalida = "openRouteNvidia2.csv"
#modeloAProbar = "cohere/north-mini-code:free"
#archivoSalida = "openRouterCohere.csv"

#Top de Open Router (pay)
#modeloAProbar = "xiaomi/mimo-v2.5"
#archivoSalida = "openRouterMimo.csv"
#modeloAProbar = "minimax/minimax-m3"
#archivoSalida = "openRouterMiniMax.csv"
#modeloAProbar = "z-ai/glm-5.2"
#archivoSalida = "openRouterZ.csv"
#modeloAProbar = "deepseek/deepseek-v4-flash"
#archivoSalida = "openRouterDeepSeek.csv"
#modeloAProbar = "anthropic/claude-sonnet-4.6"
#archivoSalida = "openRouterClaude1.csv"
#modeloAProbar = "anthropic/claude-opus-4.8" #-> gasta demasiado
#archivoSalida = "openRouterClaude2.csv"
#modeloAProbar = "openai/gpt-5.5"
#archivoSalida = "openRouterGPT2.csv"
modeloAProbar = "google/gemini-3-flash-preview"
archivoSalida = "openRouterGemini.csv"
archivoEntrada = "datos_cmd_limpio.json"

print("Cargando variables...")
load_dotenv()
api_key = os.getenv('OPEN_ROUTER_API_KEY')
url = "https://openrouter.ai/api/v1/chat/completions"
headers = {
#    "Content-Type": "application/json",
    "Authorization": f"Bearer {api_key}"
}
try:
    with open(archivoEntrada, "r", encoding="utf-8") as archivo:
        variables = json.load(archivo)
    print("Variables cargadas exitosamente.")
except Exception as e:
    print(f"Error al leer archivo JSON: {e}")
    exit()
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
6. Campos Vacíos: Si un modificador no aplica o no se menciona, utiliza el valor null (sin comillas). Si una lista o arreglo no tiene elementos, utiliza un arreglo vacío [].
7. "explicacion": Breve resumen final de la lógica aplicada tras la extracción.

### ESTRUCTURA JSON REQUERIDA (Esquema estricto):
{
  "analisis_previo": "Razonamiento paso a paso: 1) Entender el escenario clínico... 2) Aislar el diagnóstico principal... 3) Detectar modificadores... 4) Buscar patologías secundarias...",
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

Ejemplo 1:
Edad del paciente: 51
Especialidad médica: Medicina Interna
Diagnóstico clínico: Várices esofágicas secundarias con hemorragia

{
  "analisis_previo": "Razonamiento paso a paso: 1) El núcleo de la afección es la presencia de várices esofágicas secundarias. 2) Detecto el conector clave 'con', el cual indica una complicación o enfermedad secundaria asociada. 3) La palabra 'hemorragia' se aísla como enfermedad secundaria. 4) No hay modificadores de tiempo, gravedad o lateralidad explícitos. No hay ruido clínico.",
  "contexto": {
    "edad": "51",
    "especialidad": "Medicina Interna"
  },
  "diagnostico_principal": "Várices esofágicas secundarias",
  "poscoordinacion": {
    "modificadores": {
      "lateralidad": null,
      "temporalidad": null,
      "gravedad": null,
      "anatomia_especifica": null,
      "otros": []
    },
    "enfermedades_secundarias": [
      "Hemorragia"
    ]
  },
  "ruido_clinico": [],
  "explicacion": "Se separó la condición principal de su complicación (hemorragia) utilizando el conector 'con', mapeándolo correctamente al eje de enfermedades secundarias."
}

Ejemplo 2:
Edad del paciente: 75
Especialidad médica: Sin definir
Diagnóstico clínico: Neumonía, organismo sin especificación

{
  "analisis_previo": "Razonamiento paso a paso: 1) La afección núcleo evidente es la neumonía. 2) La frase 'organismo sin especificación' actúa como un modificador descriptivo sobre la etiología (causa) de la neumonía. 3) No hay presencia de otras patologías secundarias ni conectores que indiquen comorbilidades. 4) No se detecta ruido clínico.",
  "contexto": {
    "edad": "75",
    "especialidad": "Sin definir"
  },
  "diagnostico_principal": "Neumonía",
  "poscoordinacion": {
    "modificadores": {
      "lateralidad": null,
      "temporalidad": null,
      "gravedad": null,
      "anatomia_especifica": null,
      "otros": [
        "organismo sin especificación"
      ]
    },
    "enfermedades_secundarias": []
  },
  "ruido_clinico": [],
  "explicacion": "El diagnóstico es una entidad principal única. La información sobre el microorganismo se extrae como un modificador etiológico, dejando vacías las enfermedades secundarias."
}

### TEXTO CLÍNICO A PROCESAR:
Edad del paciente: {edad}
Especialidad médica: {especialidad}
Diagnóstico clínico: {diagnostico}
"""

print("Iniciando pruebas...")

with open(archivoSalida, "w", newline="", encoding="utf-8") as archivoCSV:
    escritor = csv.writer(archivoCSV, delimiter=";")
    
    # 6 columnas exactas para cuadrar los datos
    escritor.writerow(["diagnostico_principal", "contexto", "poscoordinacion", "ruido_clinico", "tiempo_respuesta", "explicacion"])
    
    for ejemplo in variables:
#    if 1==1:
#        ejemplo = variables[0]
        diagnostico_texto = ejemplo["text"]
        print(f"Procesando diagnóstico: {diagnostico_texto}")
        
        promtCompleto = promtBase.replace("{diagnostico}", diagnostico_texto)
        promtCompleto = promtCompleto.replace("{especialidad}", ejemplo["specialty"])
        promtCompleto = promtCompleto.replace("{edad}", str(ejemplo["age"]))
        
        tiempoInicio = time.time()
        
        try:
            data = {
              "model": modeloAProbar, 
              "messages": [
                {"role": "user", "content": promtCompleto}
              ],
              "temperature": 0.0
              }
            max_reintentos = 3
            textoRespuesta = None
            for intento in range(max_reintentos):
              respuesta = requests.post(url, headers=headers, json=data)
              if respuesta.status_code == 200:
                # Petición exitosa
                textoRespuesta = respuesta.json()['choices'][0]['message']['content']
                print("¡Respuesta recibida con éxito!")
                break # Salimos del bucle
              elif respuesta.status_code == 429:
                datos_error = respuesta.json()
        
                # Intentamos extraer los segundos de espera del error, si no, esperamos 20s por defecto
                try:
                  espera = datos_error['error']['metadata']['retry_after_seconds']
                except (KeyError, ValueError):
                  espera = 20 
            
                print(f"Límite de la API alcanzado. Esperando {espera} segundos antes de reintentar...")
                time.sleep(espera)
              else:
                # Otro tipo de error (400, 401, 500, etc.)
                print(f"Error definitivo: {respuesta.status_code} - {respuesta.text}")
                break
            """
            respuesta = ollama.chat(
                model=modeloAProbar, 
                messages=[{"role": "user", "content": promtCompleto}],
                options={
                    'temperature': 0.0, 
                    'num_ctx': 4096     
                }
            )
            textoRespuesta = respuesta.message.content
            """
            if respuesta.status_code == 200:
              # La API de OpenRouter devuelve un JSON estructurado de forma diferente a Ollama
              datos_json = respuesta.json()
              textoRespuesta = datos_json['choices'][0]['message']['content']
            else:
              # Manejo básico de errores por si falla la llamada
              print(f"Error en la petición: {respuesta.status_code} - {respuesta.text}")
              textoRespuesta = None
            tiempoFin = time.time()
            tiempoTotal = round(tiempoFin - tiempoInicio, 2)
            """
            # Limpieza exhaustiva de markdown para prevenir errores al parsear el JSON
            texto_limpio = textoRespuesta.strip()
            if texto_limpio.startswith("```json"):
                texto_limpio = texto_limpio[7:]
            elif texto_limpio.startswith("```"):
                texto_limpio = texto_limpio[3:]
            if texto_limpio.endswith("```"):
                texto_limpio = texto_limpio[:-3]
            texto_limpio = texto_limpio.strip()
            """
            if textoRespuesta:
              # --- NUEVA LIMPIEZA EXHAUSTIVA CON REGEX ---
              # Busca todo lo que esté entre la primera '{' y la última '}'
              match = re.search(r'\{.*\}', textoRespuesta, re.DOTALL)
            
              if match:
                  texto_limpio = match.group(0)
              else:
                  # Si el modelo alucinó tanto que ni siquiera generó llaves, forzamos un error
                  raise ValueError(f"El modelo no generó un JSON. Respuesta cruda: {textoRespuesta[:50]}...")
            
              # Parseamos el JSON devuelto
            
              datos_json = json.loads(texto_limpio)
            
              # Extracción basada estrictamente en la definición del prompt
              diagnostico_principal = datos_json.get("diagnostico_principal", "No encontrado")
              explicacion = datos_json.get("explicacion", "")
            
              # Formateamos sub-objetos y listas como string para no romper el CSV
              contexto = json.dumps(datos_json.get("contexto", {}), ensure_ascii=False)
              post_coord = json.dumps(datos_json.get("poscoordinacion", {}), ensure_ascii=False)
              ruido_clinico = json.dumps(datos_json.get("ruido_clinico", []), ensure_ascii=False)
            
              escritor.writerow([
                  diagnostico_principal, 
                  contexto, 
                  post_coord, 
                  ruido_clinico, 
                  tiempoTotal,
                  explicacion
              ])
              print(f"Completado. Respuesta obtenida en {tiempoTotal} segundos.")
            
        except Exception as e:
            tiempoFin = time.time()
            tiempoTotal = round(tiempoFin - tiempoInicio, 2)
            
            # Ajustado para que lance las mismas 6 columnas en caso de error
            escritor.writerow([
                diagnostico_texto, 
                "Error en contexto", 
                "Error en poscoordinacion", 
                "Error en ruido", 
                tiempoTotal,
                f"Error al procesar JSON o API: {e}" 
            ])
            print(f"Error al procesar: {e}")

print(f"\n--- Pruebas finalizadas. Resultados guardados en '{archivoSalida}' ---")