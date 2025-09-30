#!/usr/bin/env python
"""
Script de prueba simple para verificar que el sistema de carga de datos funciona correctamente
después de las correcciones del logging
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'proyecto_automatizacion.settings')
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
django.setup()

from automatizacion.data_load_service import data_load_service
from django.db import connections
import uuid
import time


def test_data_load_simple():
    """Prueba simple del servicio de carga de datos"""
    print("=== Probando Servicio de Carga de Datos ===")
    
    try:
        # Datos de prueba simples
        test_data = [
            {
                'id': str(uuid.uuid4()),
                'nombre': 'Test User 1',
                'email': 'test1@example.com',
                'fecha_registro': '2025-09-26'
            },
            {
                'id': str(uuid.uuid4()),
                'nombre': 'Test User 2',
                'email': 'test2@example.com',
                'fecha_registro': '2025-09-26'
            }
        ]
        
        # Llamar al servicio de carga usando el método execute_data_load
        result = data_load_service.execute_data_load(
            source_database='default',
            source_table='TestTable',
            proceso_nombre='Test Data Load Simple',
            transform_func=None  # Sin transformaciones para esta prueba
        )
        
        if result['success']:
            print(f"✓ Carga exitosa - Procesados: {result['stats']['procesados']}")
            print(f"✓ Proceso ID: {result['proceso_id']}")
            
            # Verificar que se guardó en logs
            with connections['logs'].cursor() as cursor:
                cursor.execute("""
                    SELECT ProcesoID, Estado, NombreProceso, DuracionSegundos
                    FROM ProcesoLog 
                    WHERE ProcesoID = %s
                """, [result['proceso_id']])
                log_record = cursor.fetchone()
                
                if log_record:
                    print(f"✓ Log verificado - Estado: {log_record[1]}, Duración: {log_record[3]}s")
                else:
                    print("✗ No se encontró el log en la base de datos")
                    
        else:
            print(f"✗ Error en la carga: {result['error']}")
            
    except Exception as e:
        print(f"✗ Error en test_data_load_simple: {e}")
        import traceback
        traceback.print_exc()


def test_database_connections():
    """Prueba las conexiones a las bases de datos"""
    print("\n=== Probando Conexiones a Bases de Datos ===")
    
    # Test conexión a logs
    try:
        with connections['logs'].cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM ProcesoLog")
            count = cursor.fetchone()[0]
            print(f"✓ Conexión 'logs' OK - {count} registros en ProcesoLog")
    except Exception as e:
        print(f"✗ Error en conexión 'logs': {e}")
    
    # Test conexión a destino  
    try:
        with connections['destino'].cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM ResultadosProcesados")
            count = cursor.fetchone()[0]
            print(f"✓ Conexión 'destino' OK - {count} registros en ResultadosProcesados")
    except Exception as e:
        print(f"✗ Error en conexión 'destino': {e}")


def test_logging_integration():
    """Prueba específica de la integración de logging"""
    print("\n=== Probando Integración de Logging ===")
    
    try:
        from automatizacion.web_logger import registrar_proceso_web, finalizar_proceso_web
        
        # Iniciar proceso
        logger, proceso_id = registrar_proceso_web(
            nombre_proceso="Test Logging Integration",
            datos_adicionales={"test": True, "timestamp": time.time()}
        )
        
        if logger and proceso_id:
            print(f"✓ Proceso iniciado con ID: {proceso_id}")
            
            # Simular trabajo
            time.sleep(1)
            
            # Finalizar proceso
            finalizar_proceso_web(
                logger, 
                exito=True, 
                detalles="Test de integración completado exitosamente"
            )
            
            print("✓ Proceso finalizado correctamente")
            
            # Verificar en base de datos
            with connections['logs'].cursor() as cursor:
                cursor.execute("""
                    SELECT Estado, DuracionSegundos, MensajeError
                    FROM ProcesoLog 
                    WHERE ProcesoID = %s
                """, [proceso_id])
                result = cursor.fetchone()
                
                if result:
                    print(f"✓ Verificado en BD - Estado: {result[0]}, Duración: {result[1]}s")
                    if result[2]:
                        print(f"  Detalles: {result[2]}")
                else:
                    print("✗ No se encontró el registro en la base de datos")
                    
        else:
            print("✗ No se pudo iniciar el proceso de logging")
            
    except Exception as e:
        print(f"✗ Error en test_logging_integration: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    print("Iniciando pruebas del sistema corregido...")
    
    test_database_connections()
    test_logging_integration()
    test_data_load_simple()
    
    print("\n=== Todas las pruebas completadas ===")
