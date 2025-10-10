"""
Script para mostrar dónde se guardan los procesos y su estructura
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'proyecto_automatizacion.settings')
django.setup()

from automatizacion.models import MigrationProcess
from django.conf import settings

print("=" * 80)
print("📊 UBICACIÓN DE LOS PROCESOS GUARDADOS")
print("=" * 80)

# 1. Base de datos
print("\n🗄️ BASE DE DATOS:")
print(f"   Motor: {settings.DATABASES['default']['ENGINE']}")
print(f"   Archivo: {settings.DATABASES['default']['NAME']}")
print(f"   Ubicación completa: {os.path.join(settings.BASE_DIR, settings.DATABASES['default']['NAME'])}")

# 2. Tabla en la base de datos
print("\n📋 TABLA DE PROCESOS:")
print(f"   Modelo Django: MigrationProcess")
print(f"   Tabla en DB: automatizacion_migrationprocess")

# 3. Ver un proceso ejemplo
process = MigrationProcess.objects.first()
if process:
    print(f"\n📝 EJEMPLO DE PROCESO:")
    print(f"   ID: {process.id}")
    print(f"   Nombre: {process.name}")
    print(f"   Tipo: {process.source.source_type}")
    
    print(f"\n   📦 DATOS ALMACENADOS EN LA BD:")
    print(f"   ├─ name: {process.name}")
    print(f"   ├─ description: {process.description}")
    print(f"   ├─ source_id: {process.source.id} (FK a DataSource)")
    print(f"   ├─ selected_sheets: {process.selected_sheets}")
    print(f"   ├─ selected_database: {process.selected_database}")
    print(f"   ├─ selected_tables: {process.selected_tables}")
    print(f"   ├─ selected_columns: {type(process.selected_columns).__name__} con {len(process.selected_columns) if process.selected_columns else 0} items")
    print(f"   ├─ target_db_name: {process.target_db_name}")
    print(f"   ├─ status: {process.status}")
    print(f"   ├─ created_at: {process.created_at}")
    print(f"   ├─ updated_at: {process.updated_at}")
    print(f"   └─ last_run: {process.last_run}")

# 4. Contar procesos
total = MigrationProcess.objects.count()
print(f"\n📊 ESTADÍSTICAS:")
print(f"   Total de procesos guardados: {total}")

# Por tipo
from django.db.models import Count
stats = MigrationProcess.objects.values('source__source_type').annotate(count=Count('id'))
print(f"\n   Por tipo de fuente:")
for stat in stats:
    print(f"   ├─ {stat['source__source_type']}: {stat['count']} procesos")

# 5. Archivos relacionados
print(f"\n📁 ARCHIVOS RELACIONADOS (si existen):")

# Excel/CSV files
excel_processes = MigrationProcess.objects.filter(source__source_type='excel')
csv_processes = MigrationProcess.objects.filter(source__source_type='csv')

if excel_processes.exists():
    print(f"\n   📊 Archivos Excel:")
    for proc in excel_processes[:3]:
        if proc.source.file_path:
            print(f"   ├─ {proc.name}: {proc.source.file_path}")
            print(f"      └─ Existe: {'✅ Sí' if os.path.exists(proc.source.file_path) else '❌ No'}")

if csv_processes.exists():
    print(f"\n   📄 Archivos CSV:")
    for proc in csv_processes[:3]:
        if proc.source.file_path:
            print(f"   ├─ {proc.name}: {proc.source.file_path}")
            print(f"      └─ Existe: {'✅ Sí' if os.path.exists(proc.source.file_path) else '❌ No'}")

print("\n" + "=" * 80)
print("\n📌 RESUMEN:")
print("   Los procesos se guardan en:")
print(f"   1. Base de datos SQLite: {settings.DATABASES['default']['NAME']}")
print(f"   2. Tabla: automatizacion_migrationprocess")
print(f"   3. Los archivos Excel/CSV se guardan en el sistema de archivos")
print(f"   4. Las configuraciones (columnas, tablas) se guardan como JSON en la BD")
print("=" * 80)

# 6. Mostrar estructura de la tabla
print("\n🏗️ ESTRUCTURA DE LA TABLA:")
print("   Campo                  | Tipo           | Descripción")
print("   " + "-" * 70)
print("   id                     | Integer        | ID único del proceso")
print("   name                   | CharField      | Nombre del proceso")
print("   description            | TextField      | Descripción opcional")
print("   source_id              | ForeignKey     | Relación a DataSource")
print("   selected_sheets        | JSONField      | Hojas de Excel seleccionadas")
print("   selected_database      | CharField      | Base de datos SQL seleccionada")
print("   selected_tables        | JSONField      | Tablas SQL seleccionadas")
print("   selected_columns       | JSONField      | Columnas por tabla/hoja")
print("   target_db_name         | CharField      | Base de datos destino")
print("   target_db_connection   | ForeignKey     | Conexión destino (opcional)")
print("   target_table           | CharField      | Tabla destino (opcional)")
print("   status                 | CharField      | Estado del proceso")
print("   created_at             | DateTimeField  | Fecha de creación")
print("   updated_at             | DateTimeField  | Última modificación")
print("   last_run               | DateTimeField  | Última ejecución")
print("   allow_rollback         | BooleanField   | Permitir rollback")
print("   last_checkpoint        | JSONField      | Punto de restauración")
print("=" * 80)
