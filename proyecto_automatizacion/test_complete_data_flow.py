import os
import django
import sys

# Configurar Django
sys.path.append(r'c:\Users\migue\OneDrive\Escritorio\DJANGO DE NUEVO\opav\proyecto_automatizacion')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'proyecto_automatizacion.settings')
django.setup()

from automatizacion.models import MigrationProcess
from django.db import connections

def test_isaac5_with_data():
    """
    Prueba el proceso 'proceso isaac 5' ahora que la tabla fuente tiene datos reales
    """
    
    print("=== PRUEBA COMPLETA DE INSERCIÓN CON DATOS REALES ===")
    
    try:
        # Obtener el proceso
        process = MigrationProcess.objects.get(name='proceso isaac 5')
        
        print(f"✅ Proceso encontrado: '{process.name}' (ID: {process.id})")
        
        # Ejecutar el proceso
        print(f"\n🚀 Ejecutando proceso con datos reales...")
        process.run()
        
        # Verificar el resultado en DestinoAutomatizacion
        print(f"\n🔍 Verificando tabla creada en DestinoAutomatizacion...")
        
        try:
            connection = connections['destino']
            cursor = connection.cursor()
            
            table_name = 'proceso_isaac_5_dbo_Usuarios'
            
            # Verificar que la tabla existe
            cursor.execute(f"""
                SELECT COUNT(*) 
                FROM INFORMATION_SCHEMA.TABLES 
                WHERE TABLE_NAME = '{table_name}'
            """)
            
            table_exists = cursor.fetchone()[0] > 0
            
            if not table_exists:
                print(f"❌ La tabla '{table_name}' no existe en DestinoAutomatizacion")
                return
            
            print(f"✅ Tabla '{table_name}' encontrada")
            
            # Contar registros
            cursor.execute(f"SELECT COUNT(*) FROM [{table_name}]")
            count = cursor.fetchone()[0]
            
            print(f"📊 Total registros en tabla destino: {count}")
            
            if count > 0:
                # Mostrar los datos insertados
                cursor.execute(f"SELECT * FROM [{table_name}]")
                rows = cursor.fetchall()
                column_names = [desc[0] for desc in cursor.description]
                
                print(f"📋 Datos insertados correctamente:")
                print(f"   Columnas: {column_names}")
                
                for i, row in enumerate(rows, 1):
                    print(f"   Fila {i}:")
                    for j, value in enumerate(row):
                        col_name = column_names[j] if j < len(column_names) else f'Col_{j}'
                        print(f"      {col_name}: {value}")
                
                print(f"\n🎉 ¡ÉXITO! Los datos se insertaron correctamente.")
                print(f"   ✅ Tabla creada: {table_name}")
                print(f"   ✅ Registros insertados: {count}")
                print(f"   ✅ Estructura correcta: {len(column_names)} columnas")
                
            else:
                print(f"❌ La tabla existe pero no tiene datos (0 registros)")
                
                # Verificar estructura al menos
                cursor.execute(f"""
                    SELECT COLUMN_NAME, DATA_TYPE 
                    FROM INFORMATION_SCHEMA.COLUMNS 
                    WHERE TABLE_NAME = '{table_name}' 
                    ORDER BY ORDINAL_POSITION
                """)
                
                columns = cursor.fetchall()
                print(f"📋 Estructura de la tabla:")
                for col_name, data_type in columns:
                    print(f"   - {col_name} ({data_type})")
        
        except Exception as db_error:
            print(f"❌ Error verificando base de datos: {db_error}")
        
    except MigrationProcess.DoesNotExist:
        print(f"❌ No se encontró el proceso 'proceso isaac 5'")
    except Exception as e:
        print(f"❌ Error durante la prueba: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_isaac5_with_data()