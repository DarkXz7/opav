import os
import sys
import django

# Configurar entorno Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'proyecto_automatizacion.settings')
django.setup()

from automatizacion.models import MigrationProcess
from automatizacion.utils import SQLServerConnector

def list_available_tables_and_fix_process(process_id):
    """
    Lista tablas disponibles en la base de datos SQL y
    actualiza el proceso para usar una tabla existente
    """
    try:
        process = MigrationProcess.objects.get(id=process_id)
        print(f"\n===== FIXING PROCESS '{process.name}' (ID: {process_id}) =====")
        
        # Verificar source y conexión
        if not process.source or process.source.source_type != 'sql':
            print(f"El proceso {process.name} no es de tipo SQL o no tiene fuente configurada")
            return False
            
        if not process.source.connection:
            print("No hay conexión SQL configurada")
            return False
            
        connection = process.source.connection
        print(f"Conectando a SQL Server: {connection.server}/{connection.selected_database}")
        
        # Conectar a la base de datos
        connector = SQLServerConnector(
            connection.server,
            connection.username,
            connection.password,
            connection.port
        )
        
        if not connector.select_database(connection.selected_database):
            print(f"No se pudo conectar a la base de datos {connection.selected_database}")
            return False
            
        # Obtener lista de tablas
        try:
            tables = connector.list_tables()
            if not tables:
                print("No se encontraron tablas en la base de datos")
                return False
                
            print(f"\nTablas disponibles en {connection.selected_database}:")
            for i, table in enumerate(tables, 1):
                print(f"{i}. {table}")
                
            # Seleccionar la primera tabla disponible
            selected_table = tables[0]
            print(f"\n✅ Seleccionando automáticamente la tabla: {selected_table}")
            
            # Actualizar el proceso
            process.selected_tables = [selected_table]
            process.save()
            
            print(f"\n✅ Proceso '{process.name}' actualizado correctamente.")
            print(f"Ahora está configurado para usar la tabla: {process.selected_tables}")
            
            return True
            
        except Exception as e:
            print(f"Error al obtener tablas: {str(e)}")
            return False
        finally:
            try:
                connector.disconnect()
            except:
                pass
            
    except MigrationProcess.DoesNotExist:
        print(f"No se encontró ningún proceso con ID {process_id}")
        return False
    except Exception as e:
        print(f"Error general: {str(e)}")
        return False

if __name__ == "__main__":
    process_id = 34  # CESAR_10
    list_available_tables_and_fix_process(process_id)