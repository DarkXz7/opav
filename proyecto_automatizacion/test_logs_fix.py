#!/usr/bin/env python
"""
Script de prueba para verificar que el logging funciona correctamente
después de las correcciones de los campos del modelo ProcesoLog
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'proyecto_automatizacion.settings')
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
django.setup()

from automatizacion.logs.utils import ProcesoLogger, registrar_evento
from automatizacion.web_logger import registrar_proceso_web, finalizar_proceso_web


def test_proceso_logger():
    """Prueba la clase ProcesoLogger"""
    print("=== Probando ProcesoLogger ===")
    
    try:
        logger = ProcesoLogger("Test Proceso Logger")
        proceso_id = logger.iniciar({"test_param": "test_value"})
        print(f"✓ Proceso iniciado con ID: {proceso_id}")
        
        # Simular éxito
        logger.finalizar_exito("Proceso completado exitosamente")
        print("✓ Proceso finalizado con éxito")
        
    except Exception as e:
        print(f"✗ Error en ProcesoLogger: {e}")
        import traceback
        traceback.print_exc()


def test_registrar_evento():
    """Prueba la función registrar_evento"""
    print("\n=== Probando registrar_evento ===")
    
    try:
        evento_id = registrar_evento(
            nombre_evento="Test Event",
            estado="Completado",
            parametros={"test": "data"},
            error=None
        )
        print(f"✓ Evento registrado con ID: {evento_id}")
        
    except Exception as e:
        print(f"✗ Error en registrar_evento: {e}")
        import traceback
        traceback.print_exc()


def test_web_logger():
    """Prueba las funciones de web_logger"""
    print("\n=== Probando web_logger ===")
    
    try:
        logger, proceso_id = registrar_proceso_web(
            nombre_proceso="Test Web Process",
            datos_adicionales={"frontend": True}
        )
        print(f"✓ Proceso web iniciado con ID: {proceso_id}")
        
        if logger:
            finalizar_proceso_web(logger, exito=True, detalles="Test completado")
            print("✓ Proceso web finalizado con éxito")
        else:
            print("✗ Logger no se pudo crear")
            
    except Exception as e:
        print(f"✗ Error en web_logger: {e}")
        import traceback
        traceback.print_exc()


def test_error_handling():
    """Prueba el manejo de errores"""
    print("\n=== Probando manejo de errores ===")
    
    try:
        logger = ProcesoLogger("Test Error Handling")
        proceso_id = logger.iniciar({"test_error": True})
        print(f"✓ Proceso de error iniciado con ID: {proceso_id}")
        
        # Simular error
        logger.finalizar_error("Error simulado para testing")
        print("✓ Error registrado correctamente")
        
    except Exception as e:
        print(f"✗ Error en manejo de errores: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    print("Iniciando pruebas de logging después de correcciones...")
    
    test_proceso_logger()
    test_registrar_evento()
    test_web_logger()
    test_error_handling()
    
    print("\n=== Pruebas completadas ===")
