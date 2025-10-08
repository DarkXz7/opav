import os
import django

# Configurar entorno Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'proyecto_automatizacion.settings')
django.setup()

from automatizacion.models import MigrationProcess

def fix_selected_tables_direct(process_id, table_name='Employees'):
    """
    Corrige el campo selected_tables de un proceso directamente con un valor específico
    """
    try:
        process = MigrationProcess.objects.get(id=process_id)
        print(f"\nProceso actual: {process.name} (ID: {process_id})")
        print(f"Selected tables antes: {process.selected_tables}")
        
        # Actualizar el campo selected_tables con una tabla por defecto
        # Esto es solo para probar - normalmente deberías usar tablas reales
        process.selected_tables = [table_name]
        process.save()
        
        print(f"Selected tables después: {process.selected_tables}")
        print(f"\nProceso '{process.name}' actualizado con éxito.")
        print(f"Se han seleccionado {len(process.selected_tables)} tablas.")
        print(f"\nAhora puede intentar ejecutar el proceso nuevamente desde la interfaz web:")
        print(f"http://127.0.0.1:8000/automatizacion/process/{process_id}/")
        
    except MigrationProcess.DoesNotExist:
        print(f"No se encontró ningún proceso con ID {process_id}")
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    # Corrige el proceso CESAR_10 (ID 34)
    fix_selected_tables_direct(34, 'dbo.Employees')  # Usa una tabla que exista en tu base de datos