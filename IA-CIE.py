import ollama
import csv
import time
import json
#modeloAProbar = "llama3.1:8b"
#archivoSalida = "resultadosLlama3.1.csv"
modeloAProbar = "phi4"
archivoSalida = "resultadosPhi4.csv"
#modeloAProbar = "mistral-small"
#archivoSalida = "resultadosMistralSmall.csv"
#modeloAProbar = "gemma3:27b"
#archivoSalida = "resultadosGemma3.csv"
#modeloAProbar = "qwen3.5:9b"
#archivoSalida = "resultadosQwen3.5.csv"
#modeloAProbar = "gpt-oss:20b"
#archivoSalida = "resultadosGptOss.csv"
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
Actúa como un experto en codificación médica y especialista en la CIE-11 de la OMS, así como un experto en estructuración de datos JSON.
Tu tarea es analizar un diagnóstico clínico proporcionado en texto libre y asignar el código CIE-11 más preciso, utilizando la post-coordinación (clústeres) cuando sea necesario. Para mejorar la precisión, debes tomar en cuenta la edad del paciente y la especialidad médica.
Reglas de codificación y formato que debes seguir estrictamente:
Exactitud: Solo proporciona códigos CIE-11 válidos y oficiales. No inventes códigos.
Post-coordinación: Identifica y aplica los códigos de extensión (lateralidad, gravedad, anatomía, tipo de fractura, etc.) si la información clínica lo permite. Únelos correctamente en el codigo_uri_completo usando el formato estándar de la CIE-11 (usualmente con el símbolo & para clústeres).
Contexto: Utiliza la edad y la especialidad para desambiguar términos.
Incertidumbre: Si el diagnóstico es vago, asigna el código de la categoría general más adecuada y explícalo brevemente en el campo "explicacion".
FORMATO DE SALIDA ESTRICTO: Debes responder ÚNICAMENTE con un objeto JSON válido. No incluyas saludos, explicaciones fuera del JSON, ni formato Markdown adicional (ni siquiera los bloques ```json).
Estructura JSON requerida (Usa esto como tu esquema exacto):
{
"codigo_principal": {
"codigo": "Código base alfanumérico",
"nombre": "Nombre oficial en CIE-11"
},
"post_coordinacion": [
{
"codigo": "Código de extensión",
"nombre": "Significado de la extensión",
"tipo": "Categoría de la extensión (ej. Lateralidad)"
}
],
"codigo_uri_completo": "Código base unido a las extensiones (ej. NC72&XK8G&XJ44)",
"explicacion": "Breve justificación de los códigos asignados basada en el texto, edad y especialidad."
}
(Nota: Si no hay post-coordinación aplicable, devuelve el array "post_coordinacion" vacío [] y el "codigo_uri_completo" será igual al código principal).
Entrada de datos:
Diagnóstico en texto libre: {diagnostico}
Especialidad: {especialidad}
Edad del paciente: {edad}
"""
#DESPUES PROBAR ESTE OTRO PROMPT, QUE ES MÁS DETALLADO Y EXPLÍCITO EN LA ESTRUCTURA DE LOS DATOS A EXTRAER, PARA VER SI OBTENEMOS MEJORES RESULTADOS:
promtBase = """
Actúa como un médico experto en codificación clínica, especialista en la CIE-11 de la OMS, y arquitecto de datos JSON.

Tu tarea es analizar un diagnóstico clínico en texto libre, razonar sobre su estructura clínica y asignar el clúster de códigos CIE-11 más preciso, utilizando post-coordinación cuando aplique. La edad del paciente y la especialidad médica te ayudarán a desambiguar términos.

REGLAS DE CODIFICACIÓN CIE-11 (SÍGUELAS ESTRICTAMENTE):
1. Exactitud: Solo proporciona códigos oficiales. Si el diagnóstico es vago, usa el código de categoría más cercano a "sin especificar".
2. Conectores y Patologías Secundarias: Presta especial atención a palabras como "con", "asociado a", "secundario a", "debido a". Esto indica múltiples condiciones o manifestaciones que deben ir en el mismo clúster.
3. Sintaxis de Post-coordinación: 
   - Usa la barra diagonal ( / ) para unir dos códigos troncales (patología principal + secundaria/manifestación).
   - Usa el ampersand ( & ) para añadir códigos de extensión (lateralidad, gravedad, anatomía).
   - Ejemplo válido: [CódigoTroncal1]/[CódigoTroncal2]&[Extensión1]&[Extensión2]

MINI-DICCIONARIO DE EXTENSIONES COMUNES (Usa estos si aplican, no los inventes):
- Lateralidad: Derecha (XK9K), Izquierda (XK8G), Bilateral (XK9J).
- Curso Temporal: Agudo (XT8W), Crónico (XT5R), Recurrente (XT4Z).
- Gravedad: Leve (XS5W), Moderado (XS0T), Grave/Severo (XS25).

FORMATO DE SALIDA ESTRICTO:
Debes responder ÚNICAMENTE con un objeto JSON válido. No incluyas saludos, ni explicaciones fuera del JSON, ni bloques de formato markdown como ```json.

Estructura JSON requerida:
{
  "analisis_previo": "Analiza paso a paso el diagnóstico. 1) Identifica la condición principal considerando la especialidad y edad. 2) Identifica condiciones secundarias (busca la palabra 'con' o similares). 3) Identifica modificadores (lateralidad, gravedad, tiempo).",
  "diagnosticos_troncales": [
    {
      "codigo": "Código base alfanumérico principal o secundario",
      "nombre": "Nombre oficial"
    }
  ],
  "post_coordinacion": [
    {
      "codigo": "Código de extensión (ej. XK8G)",
      "nombre": "Significado de la extensión",
      "tipo": "Categoría (ej. Lateralidad, Gravedad, Curso temporal)"
    }
  ],
  "codigo_uri_completo": "Clúster final aplicando la regla de sintaxis (ej. 1A00/2B11&XK8G). Si solo hay un código troncal y sin extensiones, pon solo ese código.",
  "nivel_de_certeza": "Alta, Media o Baja (indica qué tan seguro estás de la exactitud del código)"
}

Entrada de datos:
Diagnóstico en texto libre: {diagnostico}
Especialidad: {especialidad}
Edad del paciente: {edad}
"""
print("Iniciando pruebas...")
with open(archivoSalida, "w", newline="", encoding="utf-8") as archivoCSV:
    escritor = csv.writer(archivoCSV, delimiter=";")
    escritor.writerow(["diagnostico", "codigo_principal", "post_coordinacion", "codigo_ia", "codigo_real", "explicacion", "tiempo_respuesta"])
    
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
            cod_prin_cod = datos_json.get("codigo_principal", {})
            post_coord = json.dumps(datos_json.get("post_coordinacion", []), ensure_ascii=False)
            uri_completo = datos_json.get("codigo_uri_completo", "")
            explicacion = datos_json.get("explicacion", "")
            escritor.writerow([
                diagnostico, 
                cod_prin_cod, 
                post_coord, 
                uri_completo, 
                ejemplo["code"],
                explicacion, 
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