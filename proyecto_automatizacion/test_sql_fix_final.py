import os
import django
import sys

# Añadir la ruta del proyecto al sys.path
sys.path.append(r'c:\Users\migue\OneDrive\Escritorio\DJANGO DE NUEVO\opav\proyecto_automatizacion')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'proyecto_automatizacion.settings')

# Configurar Django
django.setup()

from automatizacion.models import MigrationProcess

def run_test():
    """
    Ejecuta el proceso de migración 'miguelinho5544' para verificar la corrección.
    """
    process_name = 'miguelinho5544'
    print(f"--- Iniciando prueba para el proceso: '{process_name}' ---")
    
    try:
        # Obtener el proceso de migración
        process = MigrationProcess.objects.get(name=process_name)
        print(f"✅ Proceso '{process.name}' encontrado.")
        
        # Ejecutar el proceso
        print("🚀 Ejecutando el método run()...")
        process.run()
        print(f"--- Prueba para '{process_name}' finalizada. ---")
        
    except MigrationProcess.DoesNotExist:
        print(f"❌ ERROR: No se encontró el proceso de migración con el nombre '{process_name}'.")
        print("   Por favor, asegúrese de que el proceso exista en la base de datos.")
    except Exception as e:
        print(f"❌ ERROR INESPERADO durante la ejecución de la prueba: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    run_test()
