import os
import django

# Configurar entorno Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'proyecto_automatizacion.settings')
django.setup()

from automatizacion.models import MigrationProcess
from automatizacion.utils import SQLServerConnector

def list_available_tables(process_id):
    """Lista tablas disponibles en la conexión SQL de un proceso"""
    try:
        process = MigrationProcess.objects.get(id=process_id)
        if not process.source or process.source.source_type != 'sql':
            print(f"El proceso {process.name} no es de tipo SQL")
            return None
            
        if not process.source.connection:
            print("No hay conexión SQL configurada")
            return None
            
        connection = process.source.connection
        print(f"Conectando a SQL Server: {connection.server}/{connection.selected_database}")
        
        connector = SQLServerConnector(
            connection.server,
            connection.username,
            connection.password,
            connection.port
        )
        
        # Conectar a la base de datos
        if not connector.select_database(connection.selected_database):
            print(f"No se pudo conectar a la base de datos {connection.selected_database}")
            return None
            
        # Obtener lista de tablas
        tables = connector.list_tables()
        print(f"\nTablas disponibles en {connection.selected_database}:")
        for i, table in enumerate(tables, 1):
            print(f"{i}. {table}")
            
        return tables
        
    except MigrationProcess.DoesNotExist:
        print(f"No se encontró ningún proceso con ID {process_id}")
        return None
    except Exception as e:
        print(f"Error: {str(e)}")
        return None

def fix_selected_tables(process_id, table_names=None):
    """
    Corrige el campo selected_tables de un proceso
    Si table_names es None, intentará obtener la lista de tablas disponibles
    """
    try:
        process = MigrationProcess.objects.get(id=process_id)
        print(f"\nProceso actual: {process.name} (ID: {process_id})")
        print(f"Selected tables antes: {process.selected_tables}")
        
        # Si no se proporcionan nombres de tabla, intentar obtener la lista
        if not table_names:
            tables = list_available_tables(process_id)
            if tables and len(tables) > 0:
                # Preguntar al usuario qué tablas quiere seleccionar
                print("\nSeleccione las tablas que desea incluir (números separados por comas):")
                selection = input("> ")
                try:
                    indices = [int(idx.strip()) - 1 for idx in selection.split(',')]
                    table_names = [tables[idx] for idx in indices if 0 <= idx < len(tables)]
                except:
                    print("Entrada inválida. No se seleccionaron tablas.")
                    return
        
        if not table_names:
            print("No se seleccionaron tablas. Operación cancelada.")
            return
            
        # Actualizar el campo selected_tables
        process.selected_tables = table_names
        process.save()
        
        print(f"Selected tables después: {process.selected_tables}")
        print(f"\nProceso '{process.name}' actualizado con éxito.")
        print(f"Se han seleccionado {len(process.selected_tables)} tablas.")
        
    except MigrationProcess.DoesNotExist:
        print(f"No se encontró ningún proceso con ID {process_id}")
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    process_id = 34  # CESAR_10
    
    # Para una corrección automática con tablas específicas, descomentar la siguiente línea
    # fix_selected_tables(process_id, ["dbo.tabla1", "dbo.tabla2"])
    
    # Para una corrección interactiva (listando tablas disponibles)
    fix_selected_tables(process_id)