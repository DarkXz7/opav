"""
Verificar de dónde vienen los logs de Kawasaki y Suzuki si no existen como MigrationProcess
"""

# Configurar Django
import os
import sys
import django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'proyecto_automatizacion.settings')
django.setup()

from automatizacion.logs.models_logs import ProcesoLog
from automatizacion.models import MigrationProcess

def main():
    print("🔍 INVESTIGACIÓN: Logs de Kawasaki/Suzuki sin MigrationProcess")
    print("=" * 65)
    
    # 1. Buscar todos los logs con Kawasaki/Suzuki
    procesos_fantasma = ['kawasaki', 'Kawasaki', 'suzuki', 'Suzuki']
    
    print("📊 LOGS CON KAWASAKI/SUZUKI:")
    
    for nombre in procesos_fantasma:
        logs_encontrados = ProcesoLog.objects.using('logs').filter(
            NombreProceso__icontains=nombre
        ).order_by('-LogID')
        
        if logs_encontrados.exists():
            print(f"\n   📋 Logs con '{nombre}' ({logs_encontrados.count()} encontrados):")
            
            for log in logs_encontrados[:5]:  # Mostrar máximo 5
                print(f"      LogID: {log.LogID}")
                print(f"      ├─ ProcesoID: {log.ProcesoID}")
                print(f"      ├─ MigrationProcessID: {log.MigrationProcessID}")
                print(f"      ├─ NombreProceso: '{log.NombreProceso}'")
                print(f"      ├─ Estado: {log.Estado}")
                print(f"      └─ Fecha: {log.FechaEjecucion}")
                
                # Analizar el ParametrosEntrada para más pistas
                if log.ParametrosEntrada:
                    try:
                        import json
                        parametros = json.loads(log.ParametrosEntrada)
                        if 'migration_process_id' in str(parametros):
                            print(f"         📝 Parámetros contienen migration_process_id")
                    except:
                        pass
                print()
        else:
            print(f"   ✅ Sin logs para '{nombre}'")
    
    # 2. Analizar específicamente los logs con MigrationProcessID = 4
    print(f"\n🎯 ANÁLISIS DE LOGS CON MigrationProcessID = 4:")
    
    logs_con_4 = ProcesoLog.objects.using('logs').filter(
        MigrationProcessID=4
    ).order_by('-LogID')[:10]
    
    print(f"   📊 {logs_con_4.count()} logs encontrados con MigrationProcessID = 4")
    
    # Agrupar por NombreProceso
    nombres_con_4 = {}
    for log in logs_con_4:
        nombre = log.NombreProceso
        if nombre not in nombres_con_4:
            nombres_con_4[nombre] = []
        nombres_con_4[nombre].append(log)
    
    print(f"\n   📋 Procesos que usan MigrationProcessID = 4:")
    for nombre, logs_list in nombres_con_4.items():
        print(f"      '{nombre}': {len(logs_list)} logs")
        
        # Ver si existe MigrationProcess con ese nombre
        try:
            proceso_real = MigrationProcess.objects.get(name=nombre)
            if proceso_real.id == 4:
                print(f"         ✅ CORRECTO: '{nombre}' SÍ tiene ID = 4")
            else:
                print(f"         ❌ INCORRECTO: '{nombre}' tiene ID = {proceso_real.id}, no 4")
        except MigrationProcess.DoesNotExist:
            print(f"         ⚠️  '{nombre}' NO EXISTE como MigrationProcess")
    
    # 3. Verificar si hay algún patrón en los logs problemáticos
    print(f"\n🔍 ANÁLISIS DETALLADO DE UN LOG PROBLEMÁTICO:")
    
    # Tomar un log específico con Kawasaki si existe
    log_kawasaki = ProcesoLog.objects.using('logs').filter(
        NombreProceso__icontains='kawasaki'
    ).first()
    
    if log_kawasaki:
        print(f"   📋 Log de Kawasaki más reciente:")
        print(f"      LogID: {log_kawasaki.LogID}")
        print(f"      MigrationProcessID: {log_kawasaki.MigrationProcessID}")
        print(f"      ParametrosEntrada: {log_kawasaki.ParametrosEntrada}")
        
        # Intentar parsear los parámetros
        if log_kawasaki.ParametrosEntrada:
            try:
                import json
                parametros = json.loads(log_kawasaki.ParametrosEntrada)
                print(f"      📝 Parámetros parseados:")
                for key, value in parametros.items():
                    if 'migration' in key.lower() or 'process' in key.lower():
                        print(f"         {key}: {value}")
            except Exception as e:
                print(f"      ❌ Error parseando parámetros: {e}")
    
    print(f"\n" + "=" * 65)
    print("🎯 CONCLUSIÓN PROBABLE:")
    print("   1. Yamaha con MigrationProcessID=4 es CORRECTO (Yamaha tiene ID=4)")
    print("   2. Kawasaki/Suzuki probablemente son:")
    print("      a) Logs antiguos de procesos que ya no existen")
    print("      b) Logs creados durante pruebas/desarrollo")
    print("      c) Logs con nombres incorrectos pero MigrationProcessID correcto")
    print("   3. El sistema actual probablemente funciona bien")
    print("   4. Necesitas crear procesos Kawasaki/Suzuki nuevos si los quieres")

if __name__ == "__main__":
    main()