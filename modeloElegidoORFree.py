import matplotlib.pyplot as plt

# ==========================================
# 1. DATOS DE LOS MODELOS (Día 4 + Nuevos)
# ==========================================
modelos = [
    'OWL', 'Nemotron 3 Ultra (550B)', 'Cohere',
    'Gemma 4 (31B)', 'Nemotron 3 Super (120B)'
]

# ¡ATENCIÓN! Reemplaza los dos últimos 0.0 con la latencia real de los nuevos modelos.
latencia = [8.3, 44.24, 12.02, 22.37, 10.34] 
exactitud = [68.18, 69.7, 70.71, 53.03, 66.16]

# Añadí dos colores nuevos (Rojo para Gemma, Púrpura para Nemotron Super)
colores = ['#2ca02c', '#1f77b4', '#ff7f0e', '#d62728', '#9467bd']
tamanos = [300, 150, 150, 150, 150] 

# ==========================================
# 2. CONFIGURACIÓN DEL GRÁFICO
# ==========================================
plt.figure(figsize=(11, 7))
plt.style.use('seaborn-v0_8-whitegrid')

# Crear el gráfico de dispersión
plt.scatter(latencia, exactitud, c=colores, s=tamanos, alpha=0.8, edgecolors='black')

# Forzar los márgenes ajustados a los nuevos datos (el eje Y ahora baja hasta 50)
plt.xlim(0, 55)   
plt.ylim(50, 75)  

# Etiquetas personalizadas para que no choquen
for i, modelo in enumerate(modelos):
    if modelo == 'Cohere':
        # Texto arriba para el de mayor exactitud[cite: 6]
        plt.annotate(modelo, (latencia[i], exactitud[i] + 0.5), fontsize=11, ha='center', fontweight='bold', color='#ff7f0e')
    elif modelo == 'Nemotron 3 Ultra (550B)':
        # Texto arriba[cite: 6]
        plt.annotate(modelo, (latencia[i], exactitud[i] + 0.5), fontsize=10, ha='center', fontweight='bold', color='#1f77b4')
    elif modelo == 'OWL':
        # Texto abajo[cite: 6]
        plt.annotate(modelo, (latencia[i], exactitud[i] - 0.7), fontsize=10, ha='center', fontweight='bold', color='#2ca02c')
    elif modelo == 'Gemma 4 (31B)':
        # Texto arriba
        plt.annotate(modelo, (latencia[i], exactitud[i] + 0.5), fontsize=10, ha='center', fontweight='bold', color='#d62728')
    elif modelo == 'Nemotron 3 Super (120B)':
        # Texto abajo
        plt.annotate(modelo, (latencia[i], exactitud[i] - 0.8), fontsize=10, ha='center', fontweight='bold', color='#9467bd')

# ==========================================
# 3. DETALLES ESTÉTICOS (Formato Tesis)
# ==========================================
plt.title('Comparativa de Modelos de IA: Exactitud vs Latencia', fontsize=14, pad=20, fontweight='bold')
plt.xlabel('Latencia Promedio (Segundos)', fontsize=12, fontweight='bold')
plt.ylabel('Exactitud Top-K (%)', fontsize=12, fontweight='bold')

# Marcar el cuadrante ideal 
plt.axvline(x=25, color='gray', linestyle='--', alpha=0.5) 
plt.axhline(y=70, color='gray', linestyle='--', alpha=0.5) 

# Texto de guía en el cuadrante verde (Reposicionado debido al nuevo rango Y)
plt.text(2, 73.5, 'Cuadrante Ideal\n(Alta Precisión, Baja Latencia)', color='green', fontsize=10, alpha=0.8)

# Guardar y mostrar
plt.tight_layout()
plt.savefig('grafico_modelos_OR_free.png', dpi=300) 
print("Gráfico guardado como 'grafico_modelos_OR_free.png'")
plt.show()