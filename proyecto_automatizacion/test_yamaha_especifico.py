"""
Test específico para el proceso Yamaha que está fallando
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

def main():
    print("🔍 TEST ESPECÍFICO: Proceso Yamaha con MigrationProcessID = 4")
    print("=" * 60)
    
    # 1. Buscar el proceso Yamaha
    try:
        proceso_yamaha = MigrationProcess.objects.get(name="Yamaha")
        print(f"📋 Proceso encontrado:")
        print(f"   ID: {proceso_yamaha.id}")
        print(f"   Nombre: {proceso_yamaha.name}")
        print(f"   Estado: {proceso_yamaha.status}")
    except MigrationProcess.DoesNotExist:
        print("❌ No se encontró proceso 'Yamaha'")
        # Listar procesos disponibles
        procesos = MigrationProcess.objects.all()
        print("📋 Procesos disponibles:")
        for p in procesos:
            print(f"   ID: {p.id} - Nombre: '{p.name}'")
        return
    
    # 2. Ver logs históricos de Yamaha
    logs_yamaha = ProcesoLog.objects.using('logs').filter(
        NombreProceso="Yamaha"
    ).order_by('-LogID')[:5]
    
    print(f"\n📊 LOGS HISTÓRICOS DE YAMAHA (últimos 5):")
    for log in logs_yamaha:
        print(f"   LogID: {log.LogID}")
        print(f"   ├─ ProcesoID: {log.ProcesoID}")
        print(f"   ├─ MigrationProcessID: {log.MigrationProcessID}")
        print(f"   ├─ Estado: {log.Estado}")
        print(f"   └─ Fecha: {log.FechaEjecucion}")
        print()
    
    # 3. Ejecutar Yamaha directamente para ver qué pasa
    print(f"🧪 TEST DIRECTO: Ejecutar Yamaha manualmente")
    print(f"   ID real de Yamaha: {proceso_yamaha.id}")
    print(f"   ¿Por qué los logs muestran MigrationProcessID = 4?")
    
    # Verificar si el proceso Yamaha tiene ID = 4
    if proceso_yamaha.id == 4:
        print(f"   ✅ EXPLICACIÓN: Yamaha SÍ tiene ID = 4, por eso es correcto")
        print(f"   El problema no era el MigrationProcessID, sino la identificación del proceso")
    else:
        print(f"   ❌ PROBLEMA: Yamaha tiene ID = {proceso_yamaha.id}, pero logs muestran 4")
        
        # Buscar qué proceso tiene ID = 4
        try:
            proceso_4 = MigrationProcess.objects.get(id=4)
            print(f"   📋 Proceso con ID=4: '{proceso_4.name}'")
            print(f"   ⚠️  ¿Se está ejecutando {proceso_4.name} en lugar de Yamaha?")
        except MigrationProcess.DoesNotExist:
            print(f"   ⚠️  No existe proceso con ID=4")
    
    # 4. Test directo de ejecución
    logs_antes = ProcesoLog.objects.using('logs').count()
    print(f"\n🚀 Ejecutando Yamaha directamente (logs antes: {logs_antes})")
    
    try:
        proceso_yamaha.run()
        
        logs_despues = ProcesoLog.objects.using('logs').count()
        print(f"   ✅ Ejecución completa (logs después: {logs_despues})")
        
        # Buscar el log más reciente
        log_nuevo = ProcesoLog.objects.using('logs').order_by('-LogID').first()
        if log_nuevo:
            print(f"   📋 LOG MÁS RECIENTE:")
            print(f"      LogID: {log_nuevo.LogID}")
            print(f"      ProcesoID: {log_nuevo.ProcesoID}")
            print(f"      MigrationProcessID: {log_nuevo.MigrationProcessID}")
            print(f"      NombreProceso: {log_nuevo.NombreProceso}")
            
            if log_nuevo.MigrationProcessID == proceso_yamaha.id:
                print(f"      ✅ SUCCESS: MigrationProcessID correcto ({proceso_yamaha.id})")
            else:
                print(f"      ❌ FALLA: MigrationProcessID incorrecto")
                print(f"         Esperado: {proceso_yamaha.id}")
                print(f"         Obtenido: {log_nuevo.MigrationProcessID}")
    
    except Exception as e:
        print(f"   ❌ Error ejecutando Yamaha: {e}")
    
    print(f"\n" + "=" * 60)
    print("🔍 ANÁLISIS:")
    print("   Si Yamaha tiene ID=4 y los logs muestran MigrationProcessID=4,")
    print("   entonces el sistema está funcionando CORRECTAMENTE.")
    print("   El 'problema' era una mala interpretación de los datos.")

if __name__ == "__main__":
    main()