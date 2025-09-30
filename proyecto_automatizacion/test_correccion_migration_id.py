"""
Test para verificar que la corrección del MigrationProcessID funcione desde el frontend
"""

# Configurar Django
import os
import sys
import django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'proyecto_automatizacion.settings')
django.setup()

from automatizacion.models import MigrationProcess, DataSource
from automatizacion.logs.models_logs import ProcesoLog
from django.contrib.auth.models import User

def main():
    print("🔧 TEST CORRECCIÓN: MigrationProcessID desde frontend")
    print("=" * 60)
    
    # 1. Crear dos procesos de prueba diferentes
    print("🏗️  Creando procesos de prueba...")
    
    # Crear fuente de datos
    data_source = DataSource.objects.create(
        name="Fuente Test MigrationID",
        source_type="csv",
        file_path="test_migration_id.csv"
    )
    
    # Proceso 1: Suzuki
    proceso_suzuki = MigrationProcess.objects.create(
        name="Suzuki Test Corregido",
        description="Proceso Suzuki para probar corrección MigrationProcessID",
        source=data_source,
        status="configured"
    )
    
    # Proceso 2: Kawasaki  
    proceso_kawasaki = MigrationProcess.objects.create(
        name="Kawasaki Test Corregido", 
        description="Proceso Kawasaki para probar corrección MigrationProcessID",
        source=data_source,
        status="configured"
    )
    
    print(f"   ✅ Proceso Suzuki creado - ID: {proceso_suzuki.id}")
    print(f"   ✅ Proceso Kawasaki creado - ID: {proceso_kawasaki.id}")
    
    # 2. Obtener conteo inicial de logs
    logs_inicial = ProcesoLog.objects.using('logs').count()
    print(f"📊 Logs iniciales: {logs_inicial}")
    
    # 3. Simular ejecución del proceso Suzuki
    print(f"\n🚀 Ejecutando proceso Suzuki (ID: {proceso_suzuki.id})...")
    try:
        proceso_suzuki.run()  # Llamada directa como lo hace la vista corregida
        print("   ✅ Proceso Suzuki ejecutado")
    except Exception as e:
        print(f"   ❌ Error ejecutando Suzuki: {e}")
    
    # 4. Simular ejecución del proceso Kawasaki
    print(f"\n🚀 Ejecutando proceso Kawasaki (ID: {proceso_kawasaki.id})...")
    try:
        proceso_kawasaki.run()  # Llamada directa como lo hace la vista corregida
        print("   ✅ Proceso Kawasaki ejecutado")
    except Exception as e:
        print(f"   ❌ Error ejecutando Kawasaki: {e}")
    
    # 5. Verificar logs creados
    logs_final = ProcesoLog.objects.using('logs').count()
    nuevos_logs = logs_final - logs_inicial
    print(f"\n📊 Logs nuevos creados: {nuevos_logs}")
    
    # 6. Buscar logs de los procesos ejecutados
    print(f"\n🔍 VERIFICANDO MigrationProcessID en logs:")
    
    # Buscar log de Suzuki
    log_suzuki = ProcesoLog.objects.using('logs').filter(
        NombreProceso=proceso_suzuki.name
    ).order_by('-LogID').first()
    
    if log_suzuki:
        print(f"   📋 LOG SUZUKI:")
        print(f"      LogID: {log_suzuki.LogID}")
        print(f"      ProcesoID: {log_suzuki.ProcesoID}")
        print(f"      MigrationProcessID: {log_suzuki.MigrationProcessID}")
        print(f"      NombreProceso: {log_suzuki.NombreProceso}")
        
        if log_suzuki.MigrationProcessID == proceso_suzuki.id:
            print(f"      ✅ SUCCESS: MigrationProcessID correcto ({proceso_suzuki.id})")
        else:
            print(f"      ❌ FALLA: MigrationProcessID incorrecto")
            print(f"         Esperado: {proceso_suzuki.id}")
            print(f"         Obtenido: {log_suzuki.MigrationProcessID}")
    else:
        print("   ❌ No se encontró log de Suzuki")
    
    # Buscar log de Kawasaki
    log_kawasaki = ProcesoLog.objects.using('logs').filter(
        NombreProceso=proceso_kawasaki.name
    ).order_by('-LogID').first()
    
    if log_kawasaki:
        print(f"   📋 LOG KAWASAKI:")
        print(f"      LogID: {log_kawasaki.LogID}")
        print(f"      ProcesoID: {log_kawasaki.ProcesoID}")
        print(f"      MigrationProcessID: {log_kawasaki.MigrationProcessID}")
        print(f"      NombreProceso: {log_kawasaki.NombreProceso}")
        
        if log_kawasaki.MigrationProcessID == proceso_kawasaki.id:
            print(f"      ✅ SUCCESS: MigrationProcessID correcto ({proceso_kawasaki.id})")
        else:
            print(f"      ❌ FALLA: MigrationProcessID incorrecto")
            print(f"         Esperado: {proceso_kawasaki.id}")
            print(f"         Obtenido: {log_kawasaki.MigrationProcessID}")
    else:
        print("   ❌ No se encontró log de Kawasaki")
    
    # 7. Resultado final
    print(f"\n" + "=" * 60)
    suzuki_ok = log_suzuki and log_suzuki.MigrationProcessID == proceso_suzuki.id
    kawasaki_ok = log_kawasaki and log_kawasaki.MigrationProcessID == proceso_kawasaki.id
    
    if suzuki_ok and kawasaki_ok:
        print("🎉 CORRECCIÓN EXITOSA:")
        print("   ✅ Suzuki se guardó con MigrationProcessID correcto")
        print("   ✅ Kawasaki se guardó con MigrationProcessID correcto") 
        print("   ✅ Cada proceso usa su propio ID - problema solucionado")
    else:
        print("❌ CORRECCIÓN INCOMPLETA:")
        if not suzuki_ok:
            print("   ❌ Suzuki tiene MigrationProcessID incorrecto")
        if not kawasaki_ok:
            print("   ❌ Kawasaki tiene MigrationProcessID incorrecto")
    
    # 8. Limpiar datos de prueba
    print(f"\n🧹 Limpiando datos de prueba...")
    proceso_suzuki.delete()
    proceso_kawasaki.delete() 
    data_source.delete()
    print("   ✅ Limpieza completada")

if __name__ == "__main__":
    main()