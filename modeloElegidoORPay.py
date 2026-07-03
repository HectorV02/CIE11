import matplotlib.pyplot as plt

# ==========================================
# 1. DATOS DE LOS MODELOS (RESTANTES + Mimo)
# ==========================================
modelos = [
    'MiniMax M3', 'DeepSeek V4 Flash', 'Claude Sonnet 4.6', 'GPT 5.5', 'Gemini 3 Flash', 'GLM 5.2', 'Mimo V2.5'
]

latencia = [13.73, 10.19, 9.32, 8.30, 3.62, 13.35, 21.9]
exactitud = [73.23, 72.22, 71.21, 68.18, 65.66, 65.66, 65.66]

# Colores distintos para cada modelo (Añadido un tono amarillo/oliva para Mimo)
colores = ['#d62728', '#9467bd', '#8c564b', '#e377c2', '#17becf', '#7f7f7f', '#bcbd22']
tamanos = [200, 200, 200, 200, 200, 200, 200] 

# ==========================================
# 2. CONFIGURACIÓN DEL GRÁFICO
# ==========================================
plt.figure(figsize=(11, 7))
plt.style.use('seaborn-v0_8-whitegrid')

# Crear el gráfico de dispersión
plt.scatter(latencia, exactitud, c=colores, s=tamanos, alpha=0.8, edgecolors='black')

# Forzar los márgenes ajustados al nuevo grupo de datos
plt.xlim(0, 25)   # Aumentado a 25 para incluir la latencia de Mimo (21.9s)
plt.ylim(63, 76)  # La exactitud va de 65.66 a 73.23, se mantiene igual

# Etiquetas personalizadas para que no choquen
for i, modelo in enumerate(modelos):
    if modelo in ['MiniMax M3', 'DeepSeek V4 Flash', 'Claude Sonnet 4.6']:
        # Textos arriba para los modelos con mayor exactitud
        plt.annotate(modelo, (latencia[i], exactitud[i] + 0.4), fontsize=10, ha='center', fontweight='bold', color=colores[i])
    elif modelo == 'Gemini 3 Flash':
        # Texto a la derecha para el más rápido (evita chocar con el borde o línea guía)
        plt.annotate(modelo, (latencia[i] + 0.5, exactitud[i] - 0.1), fontsize=10, ha='left', fontweight='bold', color=colores[i])
    elif modelo == 'Mimo V2.5':
        # Texto arriba para Mimo
        plt.annotate(modelo, (latencia[i], exactitud[i] + 0.4), fontsize=10, ha='center', fontweight='bold', color=colores[i])
    else:
        # Textos abajo para el resto (GPT 5.5, GLM 5.2)
        plt.annotate(modelo, (latencia[i], exactitud[i] - 0.7), fontsize=10, ha='center', fontweight='bold', color=colores[i])

# ==========================================
# 3. DETALLES ESTÉTICOS (Formato Tesis)
# ==========================================
plt.title('Comparativa de Modelos de IA: Exactitud vs Latencia (Grupo 2)', fontsize=14, pad=20, fontweight='bold')
plt.xlabel('Latencia Promedio (Segundos)', fontsize=12, fontweight='bold')
plt.ylabel('Exactitud Top-K (%)', fontsize=12, fontweight='bold')

# Marcar el cuadrante ideal (ajustado para este grupo)
# Umbral: Menos de 10 segundos, Más de 70% de exactitud
plt.axvline(x=10, color='gray', linestyle='--', alpha=0.5)
plt.axhline(y=70, color='gray', linestyle='--', alpha=0.5)

# Texto de guía en el cuadrante verde
plt.text(0.5, 74.8, 'Cuadrante Ideal\n(Alta Precisión, Baja Latencia)', color='green', fontsize=10, alpha=0.8)

# Guardar y mostrar
plt.tight_layout()
plt.savefig('grafico_modelos_OR_pay.png', dpi=300) 
print("Gráfico guardado como 'grafico_modelos_OR_pay.png'")
plt.show()