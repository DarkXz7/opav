"""
Verificar logs recientes para confirmar el problema persistente
"""

# Configurar Django
import os
import sys
import django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'proyecto_automatizacion.settings')
django.setup()

from automatizacion.models import MigrationProcess
from automatizacion.logs.models_logs import ProcesoLog
from datetime import datetime, timedelta

def main():
    print("🔍 VERIFICACIÓN: Logs recientes del MigrationProcessID")
    print("=" * 60)
    
    # Verificar logs de las últimas 2 horas
    hace_2_horas = datetime.now() - timedelta(hours=2)
    
    try:
        logs_recientes = ProcesoLog.objects.using('logs').filter(
            FechaEjecucion__gte=hace_2_horas
        ).order_by('-LogID')[:15]
        
        print(f"📊 LOGS DE LAS ÚLTIMAS 2 HORAS:")
        
        migration_ids_encontrados = {}
        
        for log in logs_recientes:
            print(f"   LogID: {log.LogID} | ProcesoID: {log.ProcesoID[:8]}...")
            print(f"   ├─ MigrationProcessID: {log.MigrationProcessID}")
            print(f"   ├─ NombreProceso: {log.NombreProceso}")
            print(f"   ├─ Estado: {log.Estado}")
            print(f"   └─ Fecha: {log.FechaEjecucion}")
            print()
            
            # Contar MigrationProcessID
            if log.MigrationProcessID:
                if log.MigrationProcessID not in migration_ids_encontrados:
                    migration_ids_encontrados[log.MigrationProcessID] = []
                migration_ids_encontrados[log.MigrationProcessID].append(log.NombreProceso)
        
        print(f"🎯 RESUMEN MigrationProcessID encontrados:")
        for migration_id, procesos in migration_ids_encontrados.items():
            # Buscar el proceso real
            try:
                proceso_real = MigrationProcess.objects.get(id=migration_id)
                print(f"   ID {migration_id}: '{proceso_real.name}' - Aparece en {len(procesos)} logs")
                for proceso_log in set(procesos):  # Usar set para evitar duplicados
                    print(f"      └─ Log: '{proceso_log}'")
            except MigrationProcess.DoesNotExist:
                print(f"   ID {migration_id}: ⚠️  Proceso no existe - Aparece en {len(procesos)} logs")
        
        # Verificar si el problema persiste
        if len(migration_ids_encontrados) == 1 and 4 in migration_ids_encontrados:
            print(f"\n❌ PROBLEMA CONFIRMADO: Todos los logs siguen usando MigrationProcessID = 4")
            
            # Ver desde dónde se están ejecutando
            logs_con_4 = [log for log in logs_recientes if log.MigrationProcessID == 4]
            print(f"📋 Logs con MigrationProcessID = 4:")
            for log in logs_con_4:
                print(f"   - {log.NombreProceso} (LogID: {log.LogID})")
        
        elif len(migration_ids_encontrados) > 1:
            print(f"\n✅ PROBLEMA RESUELTO: Los MigrationProcessID varían correctamente")
        
    except Exception as e:
        print(f"❌ Error consultando logs: {e}")

if __name__ == "__main__":
    main()