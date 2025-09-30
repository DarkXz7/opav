#!/usr/bin/env python
"""
Test específico para verificar el sistema de logging
"""
import os
import django
import sys

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'proyecto_automatizacion.settings')
django.setup()

def test_logging_directo():
    """
    Prueba directa del sistema de logging
    """
    print("=" * 50)
    print("PRUEBA DIRECTA DEL LOGGING")
    print("=" * 50)
    
    try:
        from automatizacion.web_logger_optimized import registrar_proceso_web, finalizar_proceso_web
        
        # Simular datos de un proceso
        print("\n1. Iniciando proceso web...")
        
        datos_proceso = {
            'migration_process_id': 17,
            'process_name': 'Test Logging Directo',
            'source_type': 'sql'
        }
        
        tracker, proceso_id = registrar_proceso_web(
            nombre_proceso="Test Logging Directo",
            usuario=None,
            datos_adicionales=datos_proceso
        )
        
        if tracker and proceso_id:
            print(f"   ✅ Proceso iniciado: {proceso_id}")
            
            # Finalizar proceso
            print("\n2. Finalizando proceso...")
            
            finalizar_proceso_web(
                tracker,
                usuario=None,
                exito=True,
                detalles="Proceso de prueba completado"
            )
            
            print("   ✅ Proceso finalizado")
            
            # Verificar en la BD
            print("\n3. Verificando en base de datos...")
            
            from automatizacion.logs.models_logs import ProcesoLog
            
            logs = ProcesoLog.objects.using('logs').filter(
                ProcesoID=proceso_id
            ).order_by('-FechaEjecucion')
            
            if logs:
                log = logs[0]
                print(f"   ✅ Log encontrado:")
                print(f"      - LogID: {log.LogID}")
                print(f"      - ProcesoID: {log.ProcesoID}")
                print(f"      - MigrationProcessID: {log.MigrationProcessID}")
                print(f"      - NombreProceso: {log.NombreProceso}")
                print(f"      - Estado: {log.Estado}")
                
                if log.ParametrosEntrada:
                    import json
                    try:
                        parametros = json.loads(log.ParametrosEntrada)
                        print(f"      - ParametrosEntrada: JSON válido con {len(parametros)} secciones")
                        return True
                    except:
                        print(f"      - ParametrosEntrada: {log.ParametrosEntrada[:100]}...")
                        return True
                else:
                    print("      - ParametrosEntrada: vacío")
                    return True
            else:
                print("   ❌ No se encontró el log")
                return False
                
        else:
            print("   ❌ No se pudo iniciar el proceso")
            return False
            
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        print(traceback.format_exc())
        return False

if __name__ == "__main__":
    exito = test_logging_directo()
    sys.exit(0 if exito else 1)