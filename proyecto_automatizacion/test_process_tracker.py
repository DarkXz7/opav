import os
import django
import sys

# Configurar entorno Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'proyecto_automatizacion.settings')
django.setup()

from automatizacion.logs.process_tracker import ProcessTracker

def test_process_tracker():
    """Test para verificar que los métodos del ProcessTracker funcionan correctamente"""
    print("🧪 Iniciando prueba de ProcessTracker...")
    
    # Crear una instancia de ProcessTracker
    tracker = ProcessTracker("test_proceso_tracker")
    
    # Probar el método iniciar
    print("\n📝 Probando método iniciar()...")
    proceso_id = tracker.iniciar({"test_param": "valor_test"})
    print(f"✅ Proceso iniciado con ID: {proceso_id}")
    
    # Probar el método actualizar_estado
    print("\n📝 Probando método actualizar_estado()...")
    tracker.actualizar_estado("EN_PROGRESO", "Probando actualización de estado")
    print("✅ Estado actualizado correctamente")
    
    # Probar el método finalizar
    print("\n📝 Probando método finalizar()...")
    try:
        tracker.finalizar("COMPLETADO", "Prueba de finalización completada")
        print("✅ Método finalizar() funciona correctamente")
    except Exception as e:
        print(f"❌ Error al llamar finalizar(): {str(e)}")
        print("El método finalizar() no existe o tiene un problema")
        return False
    
    # Probar el método finalizar_exito
    print("\n📝 Probando método finalizar_exito()...")
    try:
        tracker_exito = ProcessTracker("test_finalizar_exito")
        tracker_exito.iniciar()
        tracker_exito.finalizar_exito("Prueba de finalizar_exito completada")
        print("✅ Método finalizar_exito() funciona correctamente")
    except Exception as e:
        print(f"❌ Error al llamar finalizar_exito(): {str(e)}")
        return False
    
    # Probar el método finalizar_error
    print("\n📝 Probando método finalizar_error()...")
    try:
        tracker_error = ProcessTracker("test_finalizar_error")
        tracker_error.iniciar()
        tracker_error.finalizar_error(Exception("Error de prueba"))
        print("✅ Método finalizar_error() funciona correctamente")
    except Exception as e:
        print(f"❌ Error al llamar finalizar_error(): {str(e)}")
        return False
    
    print("\n✅ Todas las pruebas completadas con éxito!")
    return True

if __name__ == "__main__":
    success = test_process_tracker()
    sys.exit(0 if success else 1)