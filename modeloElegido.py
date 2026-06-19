import matplotlib.pyplot as plt

# ==========================================
# 1. DATOS DE LOS MODELOS (Día 4)
# ==========================================
modelos = [
    'Gemma 3 (4B)', 'MedGemma 1.5 (4B)', 'Phi 3.5 (3B)', 
    'Qwen 2.5 (7B)', 'DeepSeek R1 (7B)', 'Mistral (7B)', 'Llama 3.2 (3B)'
]

latencia = [32.37, 76.29, 44.94, 39.03, 68.99, 54.29, 8.69]
exactitud = [82.32, 82.32, 81.82, 76.26, 76.77, 73.74, 73.74]

colores = ['#2ca02c', '#1f77b4', '#1f77b4', '#ff7f0e', '#ff7f0e', '#ff7f0e', '#d62728']
tamanos = [300, 150, 150, 150, 150, 150, 150] 

# ==========================================
# 2. CONFIGURACIÓN DEL GRÁFICO
# ==========================================
plt.figure(figsize=(11, 7))
plt.style.use('seaborn-v0_8-whitegrid')

# Crear el gráfico de dispersión
plt.scatter(latencia, exactitud, c=colores, s=tamanos, alpha=0.8, edgecolors='black')

# Forzar los márgenes para dar espacio al texto (EL ARREGLO)
plt.xlim(0, 90)   # Espacio a los lados
plt.ylim(72, 85)  # Espacio arriba y abajo

# Etiquetas personalizadas para que no choquen
for i, modelo in enumerate(modelos):
    if modelo == 'Gemma 3 (4B)':
        # Texto arriba para el ganador
        plt.annotate(modelo, (latencia[i], exactitud[i] + 0.5), fontsize=11, ha='center', fontweight='bold', color='darkgreen')
    elif modelo == 'MedGemma 1.5 (4B)':
        # Texto arriba para MedGemma
        plt.annotate(modelo, (latencia[i], exactitud[i] + 0.5), fontsize=10, ha='center', fontweight='bold', color='#1f77b4')
    elif modelo == 'Llama 3.2 (3B)':
        # Texto a la derecha para que no se salga por la izquierda
        plt.annotate(modelo, (latencia[i] + 1.5, exactitud[i] - 0.2), fontsize=10, ha='left')
    else:
        # Texto abajo para el resto
        plt.annotate(modelo, (latencia[i], exactitud[i] - 0.6), fontsize=10, ha='center')

# ==========================================
# 3. DETALLES ESTÉTICOS (Formato Tesis)
# ==========================================
plt.title('Comparativa de Modelos de IA: Exactitud vs Latencia', fontsize=14, pad=20, fontweight='bold')
plt.xlabel('Latencia Promedio (Segundos)', fontsize=12, fontweight='bold')
plt.ylabel('Exactitud Top-K (%)', fontsize=12, fontweight='bold')

# Marcar el cuadrante ideal
plt.axvline(x=40, color='gray', linestyle='--', alpha=0.5)
plt.axhline(y=80, color='gray', linestyle='--', alpha=0.5)

# Texto de guía en el cuadrante verde (ajustado al nuevo límite)
plt.text(5, 83.5, 'Cuadrante Ideal\n(Alta Precisión, Baja Latencia)', color='green', fontsize=10, alpha=0.8)

# Guardar y mostrar
plt.tight_layout()
plt.savefig('grafico_modelos_tesis_corregido.png', dpi=300) 
print("Gráfico guardado como 'grafico_modelos_tesis_corregido.png'")
plt.show()