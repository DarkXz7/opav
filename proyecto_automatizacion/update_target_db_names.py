import os
import django
import sys

# Configurar Django
sys.path.append(r'c:\Users\migue\OneDrive\Escritorio\DJANGO DE NUEVO\opav\proyecto_automatizacion')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'proyecto_automatizacion.settings')
django.setup()

from automatizacion.models import MigrationProcess

def update_target_db_names():
    """
    Actualiza todos los procesos que tengan 'default' como target_db_name 
    para que usen 'DestinoAutomatizacion'
    """
    
    print("=== ACTUALIZANDO TARGET_DB_NAME DE 'default' A 'DestinoAutomatizacion' ===")
    
    try:
        # Buscar procesos con 'default'
        processes_with_default = MigrationProcess.objects.filter(target_db_name='default')
        count = processes_with_default.count()
        
        print(f"📊 Procesos encontrados con 'default': {count}")
        
        if count > 0:
            # Mostrar los procesos que se van a actualizar
            print("📋 Procesos a actualizar:")
            for process in processes_with_default:
                print(f"   - ID: {process.id}, Nombre: '{process.name}', Actual: '{process.target_db_name}'")
            
            # Actualizar todos
            updated = processes_with_default.update(target_db_name='DestinoAutomatizacion')
            
            print(f"\n✅ Actualizados exitosamente: {updated} procesos")
            
            # Verificar la actualización
            remaining = MigrationProcess.objects.filter(target_db_name='default').count()
            if remaining == 0:
                print("✅ Todos los procesos han sido actualizados correctamente")
            else:
                print(f"⚠️ Aún quedan {remaining} procesos con 'default'")
        else:
            print("✅ No hay procesos con 'default' que actualizar")
        
        # Mostrar estadísticas finales
        total_processes = MigrationProcess.objects.count()
        destino_processes = MigrationProcess.objects.filter(target_db_name='DestinoAutomatizacion').count()
        
        print(f"\n📊 Estadísticas finales:")
        print(f"   Total procesos: {total_processes}")
        print(f"   Con 'DestinoAutomatizacion': {destino_processes}")
        print(f"   Otros: {total_processes - destino_processes}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    update_target_db_names()