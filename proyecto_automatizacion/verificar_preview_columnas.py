"""
Script para verificar cómo se mostrarán las columnas del proceso arbejas
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'proyecto_automatizacion.settings')
django.setup()

from automatizacion.models import MigrationProcess

print("=" * 80)
print("🔍 PREVIEW DE COLUMNAS PARA PROCESO 'arbejas'")
print("=" * 80)

process = MigrationProcess.objects.filter(name__icontains='arbejas').first()

if process:
    print(f"\n📋 PROCESO: {process.name}")
    print(f"   ID: {process.id}")
    print(f"   Tipo: {process.source.source_type}")
    
    if process.selected_columns:
        print(f"\n📊 COLUMNAS SELECCIONADAS:")
        print(f"   {process.selected_columns}")
        
        print(f"\n🎨 CÓMO SE MOSTRARÁ EN EL ACORDEÓN:")
        print("=" * 80)
        
        for table_name, columns in process.selected_columns.items():
            print(f"\n📁 {table_name}")
            print(f"   Total columnas: {len(columns)}")
            
            # Simular la lógica del template
            if len(columns) <= 3:
                preview = ", ".join(columns)
            else:
                preview = f"{columns[0]}, {columns[1]}, {columns[2]} +{len(columns) - 3} más"
            
            print(f"   Preview: 📊 {preview}")
            print(f"   Badge: [{len(columns)} columnas]")
            
            print(f"\n   Listado completo:")
            for i, col in enumerate(columns, 1):
                print(f"      {i}. {col}")
    else:
        print("\n⚠️ No hay columnas seleccionadas")
else:
    print("\n❌ No se encontró el proceso 'arbejas'")

print("\n" + "=" * 80)

# Verificar otros procesos SQL
print("\n🔍 PREVIEW DE OTROS PROCESOS SQL:")
print("=" * 80)

sql_processes = MigrationProcess.objects.filter(source__source_type='sql').order_by('-updated_at')[:3]

for process in sql_processes:
    print(f"\n📋 {process.name} (ID: {process.id})")
    if process.selected_columns:
        for table_name, columns in process.selected_columns.items():
            if len(columns) <= 3:
                preview = ", ".join(columns)
            else:
                preview = f"{columns[0]}, {columns[1]}, {columns[2]} +{len(columns) - 3} más"
            
            print(f"   📁 {table_name}")
            print(f"      📊 {preview}")
            print(f"      [{len(columns)} columnas]")

print("\n" + "=" * 80)
