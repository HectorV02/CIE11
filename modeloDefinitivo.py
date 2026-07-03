import matplotlib.pyplot as plt

# ==========================================
# 1. DATOS DE LOS MEJORES MODELOS UNIFICADOS
# ==========================================
# Seleccionamos a los representantes más destacados de las 3 categorías
modelos = [
    'Gemma 3 (4B) [Local]',        # Campeón Absoluto
    'Llama 3.2 (3B) [Local Fast]', # Alternativa Local Rápida
    'Cohere [OR Free]',            # Mejor Gratuito en la nube
    'MiniMax M3 [OR Pay]',         # Campeón de Pago
    'DeepSeek V4 Flash [OR Pay]'   # Mejor Equilibrio Pago
]

latencia = [32.37, 8.69, 12.02, 13.73, 10.19]
exactitud = [82.32, 73.74, 70.71, 73.23, 72.22]

# Colores: Verde (Local), Naranja (Gratis), Púrpura (Pago)
colores = ['#2ca02c', '#98df8a', '#ff7f0e', '#9467bd', '#c5b0d5']
tamanos = [300, 150, 150, 200, 200] 

# ==========================================
# 2. CONFIGURACIÓN DEL GRÁFICO
# ==========================================
plt.figure(figsize=(11, 7))
plt.style.use('seaborn-v0_8-whitegrid')

# Crear el gráfico de dispersión
plt.scatter(latencia, exactitud, c=colores, s=tamanos, alpha=0.9, edgecolors='black')

# Márgenes optimizados para este nuevo grupo
plt.xlim(0, 40)   
plt.ylim(68, 85)  

# Etiquetas personalizadas
for i, modelo in enumerate(modelos):
    if 'Gemma' in modelo:
        plt.annotate(modelo, (latencia[i], exactitud[i] + 0.4), fontsize=11, ha='center', fontweight='bold', color='darkgreen')
    elif 'Llama' in modelo:
        plt.annotate(modelo, (latencia[i] + 0.6, exactitud[i] - 0.2), fontsize=10, ha='left', fontweight='bold', color='#2ca02c')
    elif 'MiniMax' in modelo:
        plt.annotate(modelo, (latencia[i], exactitud[i] + 0.4), fontsize=10, ha='center', fontweight='bold', color='#9467bd')
    elif 'DeepSeek' in modelo:
        plt.annotate(modelo, (latencia[i], exactitud[i] - 0.6), fontsize=10, ha='center', fontweight='bold', color='#754e9e')
    else:
        plt.annotate(modelo, (latencia[i], exactitud[i] - 0.6), fontsize=10, ha='center', fontweight='bold', color='#d66000')

# ==========================================
# 3. DETALLES ESTÉTICOS (Formato Tesis)
# ==========================================
plt.title('Comparativa Final de IA: Modelos Locales vs Comerciales', fontsize=14, pad=20, fontweight='bold')
plt.xlabel('Latencia Promedio (Segundos)', fontsize=12, fontweight='bold')
plt.ylabel('Exactitud Top-K (%)', fontsize=12, fontweight='bold')

# Marcar cuadrantes para análisis
plt.axvline(x=15, color='gray', linestyle='--', alpha=0.5) 
plt.axhline(y=75, color='gray', linestyle='--', alpha=0.5) 

# Textos explicativos en las áreas clave
plt.text(20, 83, 'Dominio Local\n(Alta Precisión, Mayor Latencia)', color='darkgreen', fontsize=10, alpha=0.8)
plt.text(1, 76, 'Zona API\n(Precisión Media, Alta Velocidad)', color='purple', fontsize=10, alpha=0.8)

# Guardar y mostrar
plt.tight_layout()
plt.savefig('grafico_consolidado_tesis.png', dpi=300) 
print("Gráfico guardado como 'grafico_consolidado_tesis.png'")
plt.show()