import os
import django
import sys

# Configurar Django
sys.path.append(r'c:\Users\migue\OneDrive\Escritorio\DJANGO DE NUEVO\opav\proyecto_automatizacion')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'proyecto_automatizacion.settings')
django.setup()

from automatizacion.models import MigrationProcess
from django.db import connections

def test_isaac5_process():
    """
    Prueba el proceso 'isaac 5' para verificar que los datos se inserten correctamente
    """
    process_name = 'isaac 5'
    
    print(f"=== PRUEBA DE INSERCIÓN DE DATOS PARA '{process_name}' ===")
    
    try:
        # Buscar el proceso
        process = MigrationProcess.objects.filter(name__icontains='isaac').first()
        
        if not process:
            print("❌ No se encontró ningún proceso que contenga 'isaac'")
            # Listar procesos disponibles
            processes = MigrationProcess.objects.all()
            print(f"📋 Procesos disponibles ({len(processes)}):")
            for p in processes:
                print(f"   - {p.name} (ID: {p.id}, Tipo: {p.source.source_type if p.source else 'Sin fuente'})")
            return
        
        print(f"✅ Proceso encontrado: '{process.name}' (ID: {process.id})")
        print(f"   📂 Tipo de fuente: {process.source.source_type if process.source else 'Sin fuente'}")
        print(f"   📋 Tablas seleccionadas: {process.selected_tables}")
        
        # Ejecutar el proceso
        print(f"\n🚀 Ejecutando proceso '{process.name}'...")
        process.run()
        
        # Verificar las tablas creadas en DestinoAutomatizacion
        print(f"\n🔍 Verificando tablas creadas en DestinoAutomatizacion...")
        
        connection = connections['destino']
        cursor = connection.cursor()
        
        # Buscar tablas que contengan el nombre del proceso
        process_name_clean = process.name.replace(' ', '_').lower()
        cursor.execute("""
            SELECT TABLE_NAME 
            FROM INFORMATION_SCHEMA.TABLES 
            WHERE TABLE_TYPE = 'BASE TABLE' 
            AND LOWER(TABLE_NAME) LIKE ?
        """, [f'%{process_name_clean}%'])
        
        tables_found = cursor.fetchall()
        
        if not tables_found:
            print(f"❌ No se encontraron tablas relacionadas con '{process.name}'")
            return
        
        print(f"✅ Tablas encontradas ({len(tables_found)}):")
        
        for (table_name,) in tables_found:
            print(f"\n📊 Tabla: {table_name}")
            
            # Contar registros
            cursor.execute(f"SELECT COUNT(*) FROM [{table_name}]")
            count = cursor.fetchone()[0]
            print(f"   📈 Total registros: {count}")
            
            # Obtener estructura de la tabla
            cursor.execute(f"""
                SELECT COLUMN_NAME, DATA_TYPE 
                FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_NAME = ? 
                ORDER BY ORDINAL_POSITION
            """, [table_name])
            
            columns = cursor.fetchall()
            print(f"   📋 Columnas ({len(columns)}):")
            for col_name, data_type in columns:
                print(f"      - {col_name} ({data_type})")
            
            # Mostrar primeros registros si existen
            if count > 0:
                cursor.execute(f"SELECT TOP 3 * FROM [{table_name}]")
                sample_rows = cursor.fetchall()
                
                print(f"   📊 Muestra de datos (primeras {len(sample_rows)} filas):")
                column_names = [desc[0] for desc in cursor.description]
                
                for i, row in enumerate(sample_rows):
                    print(f"      Fila {i+1}:")
                    for j, value in enumerate(row):
                        col_name = column_names[j] if j < len(column_names) else f'Col_{j}'
                        display_value = str(value)[:50] + ('...' if len(str(value)) > 50 else '') if value else '<NULL/VACIO>'
                        print(f"         {col_name}: {display_value}")
            else:
                print(f"   ⚠️ La tabla está vacía (0 registros)")
        
        print(f"\n✅ Prueba completada para proceso '{process.name}'")
        
    except Exception as e:
        print(f"❌ Error durante la prueba: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_isaac5_process()