import matplotlib.pyplot as plt

# ==========================================
# 1. DATOS DE LOS MODELOS (Día 4)
# ==========================================
modelos = [
    'OWL', 'Nemotron 3 Ultra (550B)', 'Cohere'
]

latencia = [8.3, 44.24, 12.02]
exactitud = [68.18, 69.7, 70.71]

colores = ['#2ca02c', '#1f77b4', '#ff7f0e']
tamanos = [300, 150, 150] 

# ==========================================
# 2. CONFIGURACIÓN DEL GRÁFICO
# ==========================================
plt.figure(figsize=(11, 7))
plt.style.use('seaborn-v0_8-whitegrid')

# Crear el gráfico de dispersión
plt.scatter(latencia, exactitud, c=colores, s=tamanos, alpha=0.8, edgecolors='black')

# Forzar los márgenes para dar espacio al texto ajustado a los nuevos datos
plt.xlim(0, 55)   # Límite ajustado para incluir la latencia de 44.24
plt.ylim(65, 74)  # Límite ajustado para incluir la exactitud de 68-71%

# Etiquetas personalizadas para que no choquen
for i, modelo in enumerate(modelos):
    if modelo == 'Cohere':
        # Texto arriba para el de mayor exactitud
        plt.annotate(modelo, (latencia[i], exactitud[i] + 0.4), fontsize=11, ha='center', fontweight='bold', color='#ff7f0e')
    elif modelo == 'Nemotron 3 Ultra (550B)':
        # Texto arriba
        plt.annotate(modelo, (latencia[i], exactitud[i] + 0.4), fontsize=10, ha='center', fontweight='bold', color='#1f77b4')
    elif modelo == 'OWL':
        # Texto abajo
        plt.annotate(modelo, (latencia[i], exactitud[i] - 0.6), fontsize=10, ha='center', fontweight='bold', color='#2ca02c')

# ==========================================
# 3. DETALLES ESTÉTICOS (Formato Tesis)
# ==========================================
plt.title('Comparativa de Modelos de IA: Exactitud vs Latencia', fontsize=14, pad=20, fontweight='bold')
plt.xlabel('Latencia Promedio (Segundos)', fontsize=12, fontweight='bold')
plt.ylabel('Exactitud Top-K (%)', fontsize=12, fontweight='bold')

# Marcar el cuadrante ideal (ajustado a los nuevos rangos)
plt.axvline(x=25, color='gray', linestyle='--', alpha=0.5) # Separa los modelos rápidos del lento
plt.axhline(y=70, color='gray', linestyle='--', alpha=0.5) # Marca el umbral de 70% de exactitud

# Texto de guía en el cuadrante verde (ajustado a las nuevas coordenadas)
plt.text(2, 73, 'Cuadrante Ideal\n(Alta Precisión, Baja Latencia)', color='green', fontsize=10, alpha=0.8)

# Guardar y mostrar
plt.tight_layout()
plt.savefig('grafico_modelos_OR_free.png', dpi=300) 
print("Gráfico guardado como 'grafico_modelos_OR_free.png'")
plt.show()