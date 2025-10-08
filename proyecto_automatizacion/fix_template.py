"""
Script para arreglar el template view_process.html corrupto
"""

# Leer el archivo
with open('proyecto_automatizacion/templates/automatizacion/view_process.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Encontrar donde empieza el contenido real (después de {% block content %})
start_marker = '{% block content %}'
start_index = content.find(start_marker)

if start_index == -1:
    print("No se encontró el marcador de inicio")
    exit(1)

# Buscar donde debería empezar el breadcrumb (contenido correcto)
breadcrumb_marker = '<ol class="breadcrumb">'
breadcrumb_index = content.find(breadcrumb_marker, start_index)

if breadcrumb_index == -1:
    print("No se encontró el breadcrumb")
    exit(1)

# Construir el contenido correcto
header = content[:start_index + len(start_marker)]
correct_start = '\n<div class="row mb-4">\n    <div class="col-md-12">\n        <nav aria-label="breadcrumb">\n            '
rest_of_content = content[breadcrumb_index:]

fixed_content = header + correct_start + rest_of_content

# Guardar el archivo arreglado
with open('proyecto_automatizacion/templates/automatizacion/view_process.html', 'w', encoding='utf-8') as f:
    f.write(fixed_content)

print("✅ Archivo arreglado exitosamente")
print(f"Tamaño original: {len(content)} caracteres")
print(f"Tamaño arreglado: {len(fixed_content)} caracteres")
