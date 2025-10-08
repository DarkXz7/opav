import os
import django
import pyodbc
import sys

# Configurar entorno Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'proyecto_automatizacion.settings')
django.setup()

from automatizacion.models import MigrationProcess

def list_tables_from_connection(connection):
    """Obtiene la lista de tablas disponibles en una conexión SQL Server"""
    try:
        conn_string = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={connection.server};DATABASE={connection.selected_database};UID={connection.username};PWD={connection.password}'
        
        # Establecer conexión directa
        conn = pyodbc.connect(conn_string)
        cursor = conn.cursor()
        
        # Ejecutar consulta para obtener tablas
        tables_query = """
        SELECT TABLE_SCHEMA + '.' + TABLE_NAME AS full_table_name
        FROM INFORMATION_SCHEMA.TABLES
        WHERE TABLE_TYPE = 'BASE TABLE'
        ORDER BY TABLE_SCHEMA, TABLE_NAME
        """
        
        cursor.execute(tables_query)
        tables = [row[0] for row in cursor.fetchall()]
        
        cursor.close()
        conn.close()
        
        return tables
        
    except Exception as e:
        print(f"Error obteniendo tablas: {str(e)}")
        return []

def fix_sql_process(process_id):
    """Arregla un proceso SQL con tablas reales de la base de datos"""
    try:
        process = MigrationProcess.objects.get(id=process_id)
        print(f"\n===== FIXING SQL PROCESS '{process.name}' (ID: {process_id}) =====")
        
        # Verificar source y conexión
        if not process.source or process.source.source_type != 'sql':
            print(f"❌ El proceso {process.name} no es de tipo SQL o no tiene fuente configurada")
            return False
            
        if not process.source.connection:
            print("❌ No hay conexión SQL configurada")
            return False
            
        # Obtener tablas disponibles
        tables = list_tables_from_connection(process.source.connection)
        
        if not tables:
            print("❌ No se encontraron tablas en la base de datos")
            return False
            
        print(f"\n📊 Tablas disponibles ({len(tables)}):")
        for i, table in enumerate(tables, 1):
            print(f"  {i}. {table}")
            
        # Seleccionar la primera tabla disponible
        if tables:
            selected_table = tables[0]
            print(f"\n✅ Seleccionando automáticamente la tabla: {selected_table}")
            
            # Actualizar el proceso
            old_tables = process.selected_tables
            process.selected_tables = [selected_table]
            process.save()
            
            print(f"\n✅ Proceso '{process.name}' actualizado:")
            print(f"  - Tablas anteriores: {old_tables}")
            print(f"  - Tablas actuales: {process.selected_tables}")
            
            return True
        
        return False
        
    except MigrationProcess.DoesNotExist:
        print(f"❌ No se encontró ningún proceso con ID {process_id}")
        return False
    except Exception as e:
        print(f"❌ Error general: {str(e)}")
        return False

def test_run_process(process_id):
    """Ejecuta un proceso y reporta el resultado detallado"""
    try:
        process = MigrationProcess.objects.get(id=process_id)
        print(f"\n===== EJECUTANDO PROCESO '{process.name}' (ID: {process_id}) =====")
        
        try:
            print("🚀 Iniciando ejecución...")
            process.run()
            print("✅ Proceso ejecutado con éxito")
            return True
        except Exception as e:
            print(f"❌ Error ejecutando proceso: {str(e)}")
            return False
            
    except MigrationProcess.DoesNotExist:
        print(f"❌ No se encontró ningún proceso con ID {process_id}")
        return False
        
if __name__ == "__main__":
    process_id = 34  # CESAR_10
    
    # Paso 1: Corregir el proceso con tablas reales
    fixed = fix_sql_process(process_id)
    
    if fixed:
        # Paso 2: Probar el proceso corregido
        print("\n🧪 Probando el proceso corregido...")
        success = test_run_process(process_id)
        
        if success:
            print("\n✅ TODO LISTO: Proceso corregido y ejecutado con éxito.")
            print("Ahora puede ejecutar el proceso desde la interfaz web sin errores.")
        else:
            print("\n❌ ATENCIÓN: Proceso corregido pero sigue fallando al ejecutarse.")
            print("Revise los mensajes de error para más información.")
    else:
        print("\n❌ No se pudo corregir el proceso. Revise los mensajes de error.")
        sys.exit(1)