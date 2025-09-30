"""
TEST SIMPLE: Verificar consistencia de IDs usando transferencia directa
"""

# Configurar Django
import os
import sys
import django
import uuid
from datetime import datetime

# Configurar path y Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'proyecto_automatizacion.settings')
django.setup()

from django.db import connections
from automatizacion.logs.process_tracker import ProcessTracker
from automatizacion.data_transfer_service import data_transfer_service
from automatizacion.logs.models_logs import ProcesoLog

def main():
    print("🔧 TEST SIMPLE: Verificar consistencia de IDs")
    print("=" * 60)
    
    # 1. Crear ProcessTracker para simular un proceso con MigrationProcessID
    process_name = "TestSimpleConsistencia"
    tracker = ProcessTracker(process_name)
    
    # 2. Iniciar proceso con MigrationProcessID específico
    migration_process_id = 999  # ID de prueba
    parametros = {
        'migration_process_id': migration_process_id,
        'test_type': 'consistencia_ids',
        'descripcion': 'Test para verificar que los IDs coincidan'
    }
    
    print(f"📝 Iniciando ProcessTracker para '{process_name}'...")
    proceso_id = tracker.iniciar(parametros)
    print(f"   ✅ UUID generado: {proceso_id}")
    
    # 3. Actualizar estado
    tracker.actualizar_estado('TRANSFIRIENDO', 'Preparando transferencia de datos')
    
    # 4. Transferir datos usando el mismo proceso_id
    print(f"\n🚀 Transfiriendo datos con ProcesoID: {proceso_id}")
    
    success, result_info = data_transfer_service.transfer_to_dynamic_table(
        process_name=process_name,
        proceso_id=proceso_id,  # ✅ Usar el MISMO UUID del tracker
        datos_procesados={"test": "consistencia", "timestamp": datetime.now().isoformat()},
        usuario_responsable="test_automatizado",
        metadata={"migration_process_id": migration_process_id},
        estado_proceso="COMPLETADO",
        tipo_operacion="TEST_CONSISTENCIA"
    )
    
    if not success:
        tracker.finalizar_error(Exception(f"Error en transferencia: {result_info.get('error')}"))
        print(f"❌ Error: {result_info.get('error')}")
        return
    
    table_name = result_info['table_name']
    resultado_id = result_info['resultado_id']
    
    print(f"   ✅ Transferencia exitosa")
    print(f"   📋 Tabla: {table_name}")
    print(f"   🆔 ResultadoID: {resultado_id}")
    
    # 5. Finalizar proceso
    detalles = f"Tabla: {table_name}, ResultadoID: {resultado_id}"
    tracker.finalizar_exito(detalles)
    
    # 6. Verificar en ProcesoLog
    print(f"\n🔍 VERIFICANDO ProcesoLog...")
    try:
        log_proceso = ProcesoLog.objects.using('logs').filter(ProcesoID=proceso_id).first()
        
        if log_proceso:
            print(f"   ✅ Log encontrado:")
            print(f"      LogID: {log_proceso.LogID}")
            print(f"      ProcesoID: {log_proceso.ProcesoID}")
            print(f"      MigrationProcessID: {log_proceso.MigrationProcessID}")
            print(f"      NombreProceso: {log_proceso.NombreProceso}")
            print(f"      Estado: {log_proceso.Estado}")
        else:
            print(f"   ❌ No se encontró log con ProcesoID: {proceso_id}")
            return
            
    except Exception as e:
        print(f"   ❌ Error consultando ProcesoLog: {e}")
        return
    
    # 7. Verificar en tabla dinámica
    print(f"\n🔍 VERIFICANDO TABLA DINÁMICA: {table_name}")
    try:
        with connections['destino'].cursor() as cursor:
            cursor.execute(f"""
                SELECT ResultadoID, ProcesoID, NombreProceso, EstadoProceso
                FROM [{table_name}]
                WHERE ResultadoID = %s
            """, [resultado_id])
            
            row = cursor.fetchone()
            
            if row:
                tabla_resultado_id, tabla_proceso_id, tabla_nombre_proceso, tabla_estado = row
                print(f"   ✅ Registro encontrado:")
                print(f"      ResultadoID: {tabla_resultado_id}")
                print(f"      ProcesoID: {tabla_proceso_id}")
                print(f"      NombreProceso: {tabla_nombre_proceso}")
                print(f"      EstadoProceso: {tabla_estado}")
                
                # ✅ VERIFICACIÓN CRÍTICA
                print(f"\n🎯 VERIFICACIÓN DE CONSISTENCIA:")
                
                if tabla_proceso_id.upper() == proceso_id.upper():
                    print(f"   ✅ SUCCESS: ProcesoID coincide")
                    print(f"      ProcesoLog.ProcesoID: {proceso_id}")
                    print(f"      Tabla.ProcesoID: {tabla_proceso_id}")
                else:
                    print(f"   ❌ FALLA: ProcesoID NO coincide")
                    print(f"      ProcesoLog.ProcesoID: {proceso_id}")
                    print(f"      Tabla.ProcesoID: {tabla_proceso_id}")
                
                if log_proceso.MigrationProcessID == migration_process_id:
                    print(f"   ✅ SUCCESS: MigrationProcessID correcto ({migration_process_id})")
                else:
                    print(f"   ❌ FALLA: MigrationProcessID incorrecto")
                    print(f"      Esperado: {migration_process_id}")
                    print(f"      En log: {log_proceso.MigrationProcessID}")
                
                print(f"\n" + "=" * 60)
                if (tabla_proceso_id.upper() == proceso_id.upper() and 
                    log_proceso.MigrationProcessID == migration_process_id):
                    print("🎉 CORRECCIÓN EXITOSA: Todos los IDs son consistentes")
                else:
                    print("❌ CORRECCIÓN INCOMPLETA: Hay problemas de consistencia")
                
            else:
                print(f"   ❌ No se encontró el registro con ResultadoID: {resultado_id}")
                
    except Exception as e:
        print(f"   ❌ Error consultando tabla dinámica: {e}")

if __name__ == "__main__":
    main()