"""
Script de prueba para el nuevo sistema de registro unificado de procesos
"""

import os
import django
import sys
import datetime
import time
import uuid
import traceback

# Configurar el entorno de Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'proyecto_automatizacion.settings')
django.setup()

# Importar el nuevo sistema de registro
from automatizacion.logs.process_tracker import ProcessTracker, registrar_evento_unificado

def test_process_tracker():
    print("="*80)
    print("PRUEBA DEL SISTEMA OPTIMIZADO DE REGISTRO DE PROCESOS")
    print("="*80)
    
    print("\n1. SEGUIMIENTO COMPLETO DE UN PROCESO CON MÚLTIPLES ESTADOS")
    print("-" * 60)
    
    try:
        # Crear un nuevo tracker para el proceso
        print("Iniciando nuevo proceso...")
        tracker = ProcessTracker("Proceso de prueba completo")
        proceso_id = tracker.iniciar({
            'tipo_proceso': 'prueba',
            'origen': 'script_optimización'
        })
        print(f"✓ Proceso iniciado con ID: {proceso_id}")
        
        # Simular un primer paso
        print("\nEjecutando primer paso...")
        time.sleep(1)  # Simulación de trabajo
        tracker.actualizar_estado(
            "En progreso", 
            "Procesando datos iniciales"
        )
        print("✓ Estado actualizado: En progreso")
        
        # Simular un segundo paso
        print("\nEjecutando segundo paso...")
        time.sleep(1)  # Más trabajo simulado
        tracker.actualizar_estado(
            "Avanzando",
            "Validación de datos completada"
        )
        print("✓ Estado actualizado: Avanzando")
        
        # Finalizar el proceso con éxito
        print("\nFinalizando proceso...")
        time.sleep(1)  # Finalización simulada
        tracker.finalizar_exito("Proceso completado correctamente")
        print("✓ Proceso finalizado con éxito")
        
        # Recuperar el registro para verificar
        from automatizacion.models_logs import ProcesoLog
        log_entry = ProcesoLog.objects.using('logs').get(ProcesoID=proceso_id)
        print("\nRegistro en la base de datos:")
        print(f"- LogID: {log_entry.LogID}")
        print(f"- ProcesoID: {log_entry.ProcesoID}")
        print(f"- Estado: {log_entry.Estado}")
        print(f"- Duración: {log_entry.DuracionSegundos} segundos")
        print(f"- Mensaje: {log_entry.MensajeError}")
        
        print("\nHistorial de estados (en ParametrosEntrada):")
        import json
        parametros = json.loads(log_entry.ParametrosEntrada)
        for idx, estado in enumerate(parametros.get('historial', [])):
            print(f"  {idx+1}. [{estado['timestamp']}] {estado['accion']}: {estado.get('detalles', '-')}")
        
    except Exception as e:
        print(f"❌ Error durante la prueba: {str(e)}")
        print(f"Tipo de error: {type(e).__name__}")
        print(f"Detalles: {traceback.format_exc()}")
    
    print("\n2. SIMULACIÓN DE PROCESO CON ERROR")
    print("-" * 60)
    
    try:
        # Crear un tracker para el proceso con error
        print("Iniciando proceso que fallará...")
        tracker = ProcessTracker("Proceso con error")
        proceso_id = tracker.iniciar({
            'tipo_proceso': 'prueba_error',
            'modo': 'simulación'
        })
        print(f"✓ Proceso iniciado con ID: {proceso_id}")
        
        # Simular un paso intermedio
        print("\nEjecutando paso intermedio...")
        time.sleep(1)
        tracker.actualizar_estado(
            "Procesando",
            "Ejecutando operación de riesgo"
        )
        print("✓ Estado actualizado: Procesando")
        
        # Simular un error
        print("\nSimulando error en el proceso...")
        tracker.finalizar_error("Error simulado para pruebas")
        print("✓ Proceso finalizado con error (simulado)")
        
    except Exception as e:
        print(f"❌ Error durante la prueba: {str(e)}")
        print(f"Detalles: {traceback.format_exc()}")
    
    print("\n3. REGISTRO DE EVENTO SIMPLE UNIFICADO")
    print("-" * 60)
    
    try:
        print("Registrando evento simple...")
        evento_id = registrar_evento_unificado(
            nombre_evento="Test de evento unificado",
            estado="Completado",
            parametros={"fuente": "test_optimización", "prioridad": "alta"},
            error=None
        )
        print(f"✓ Evento registrado con ID: {evento_id}")
        
    except Exception as e:
        print(f"❌ Error al registrar evento: {str(e)}")
        print(f"Detalles: {traceback.format_exc()}")
    
    print("\n4. VERIFICACIÓN DE REGISTROS EN BASE DE DATOS")
    print("-" * 60)
    
    try:
        from automatizacion.models_logs import ProcesoLog
        
        # Contar registros
        count = ProcesoLog.objects.using('logs').count()
        print(f"Total de registros en ProcesoLog: {count}")
        
        # Mostrar los últimos 5 registros
        print("\nÚltimos registros:")
        logs = ProcesoLog.objects.using('logs').order_by('-LogID')[:5]
        for log in logs:
            print(f"ID: {log.LogID}, ProcesoID: {log.ProcesoID}, Estado: {log.Estado}")
            print(f"  Fecha: {log.FechaEjecucion}, Duración: {log.DuracionSegundos}s")
            print(f"  Mensaje: {log.MensajeError if log.MensajeError else '-'}")
            print("-" * 40)
            
    except Exception as e:
        print(f"❌ Error al verificar registros: {str(e)}")
        print(f"Detalles: {traceback.format_exc()}")
    
    print("\nPrueba completada.")
    print("="*80)

if __name__ == "__main__":
    test_process_tracker()
