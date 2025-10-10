"""
Script para simular la obtención de datos de muestra del proceso arbejas
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'proyecto_automatizacion.settings')
django.setup()

from automatizacion.models import MigrationProcess
import pyodbc

print("=" * 80)
print("🔍 SIMULANDO OBTENCIÓN DE DATOS DE MUESTRA")
print("=" * 80)

process = MigrationProcess.objects.filter(name__icontains='arbejas').first()

if process:
    print(f"\n📋 PROCESO: {process.name}")
    print(f"   ID: {process.id}")
    print(f"   Tipo: {process.source.source_type}")
    
    if process.source.source_type == 'sql':
        print(f"\n🔌 CONEXIÓN:")
        print(f"   Servidor: {process.source.connection.server}")
        print(f"   Base de datos: {process.source.connection.selected_database}")
        
        if process.selected_columns:
            print(f"\n📊 TABLAS Y COLUMNAS:")
            for table_name, columns in process.selected_columns.items():
                print(f"\n   📁 {table_name}")
                print(f"      Columnas: {columns}")
                
                # Intentar obtener datos
                try:
                    conn_str = (
                        f'DRIVER={{ODBC Driver 17 for SQL Server}};'
                        f'SERVER={process.source.connection.server};'
                        f'DATABASE={process.source.connection.selected_database};'
                        f'UID={process.source.connection.username};'
                        f'PWD={process.source.connection.password}'
                    )
                    
                    print(f"\n   🔌 Conectando...")
                    conn = pyodbc.connect(conn_str, timeout=5)
                    cursor = conn.cursor()
                    
                    # Consultar datos
                    columns_str = ', '.join([f'[{col}]' for col in columns])
                    query = f"SELECT TOP 5 {columns_str} FROM {table_name}"
                    print(f"   📝 Query: {query}")
                    
                    cursor.execute(query)
                    rows = cursor.fetchall()
                    
                    print(f"\n   ✅ DATOS OBTENIDOS ({len(rows)} filas):")
                    print(f"   " + "-" * 70)
                    
                    # Mostrar header
                    header = " | ".join([f"{col:20}" for col in columns])
                    print(f"   {header}")
                    print(f"   " + "-" * 70)
                    
                    # Mostrar datos
                    for i, row in enumerate(rows, 1):
                        row_str = " | ".join([f"{str(val)[:20]:20}" for val in row])
                        print(f"   {row_str}")
                    
                    conn.close()
                    print(f"\n   ✅ Conexión cerrada exitosamente")
                    
                except Exception as e:
                    print(f"\n   ❌ ERROR: {e}")
else:
    print("\n❌ No se encontró el proceso 'arbejas'")

print("\n" + "=" * 80)
