"""
Script para verificar el campo selected_database del proceso
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'proyecto_automatizacion.settings')
django.setup()

from automatizacion.models import MigrationProcess

# Verificar proceso 34
process = MigrationProcess.objects.get(id=34)

print("=" * 70)
print(f"📋 INFORMACIÓN DEL PROCESO ID: {process.id}")
print("=" * 70)
print(f"Nombre: {process.name}")
print(f"Tipo de fuente: {process.source.source_type}")
print(f"\n🔍 ORIGEN (SQL):")
print(f"   Conexión: {process.source.connection.name}")
print(f"   Servidor: {process.source.connection.server}")
print(f"   BD de la conexión: {process.source.connection.selected_database}")
print(f"   BD seleccionada en el proceso: {process.selected_database}")  # ← Este es el campo correcto
print(f"\n🎯 DESTINO:")
print(f"   BD destino: {process.target_db_name}")
print(f"\n📊 TABLAS Y COLUMNAS:")
if process.selected_tables:
    print(f"   Tablas seleccionadas: {process.selected_tables}")
if process.selected_columns:
    print(f"   Columnas por tabla:")
    for table, columns in process.selected_columns.items():
        print(f"      - {table}: {len(columns)} columnas")
print("=" * 70)
