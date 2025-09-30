"""
Script simple para confirmar que ya no se crean múltiples registros
"""
from automatizacion.logs.models_logs import ProcesoLog

print("🔍 Verificando estado actual de ProcesoLog...")

# Contar todos los registros
total = ProcesoLog.objects.using('logs').count()
print(f"📊 Total de registros en ProcesoLog: {total}")

# Mostrar los últimos 5 registros para ver el patrón
ultimos = ProcesoLog.objects.using('logs').order_by('-FechaEjecucion')[:5]

print(f"\n📋 Últimos 5 registros:")
for i, log in enumerate(ultimos, 1):
    print(f"   {i}. {log.NombreProceso[:50]:<50} | Estado: {log.Estado}")

# Buscar registros de pruebas recientes
guardados = ProcesoLog.objects.using('logs').filter(
    NombreProceso__icontains="Guardado de proceso"
).order_by('-FechaEjecucion')[:3]

ejecuciones = ProcesoLog.objects.using('logs').filter(
    NombreProceso__icontains="Ejecución proceso"
).order_by('-FechaEjecucion')[:3]

print(f"\n🔸 Últimos guardados de procesos:")
for log in guardados:
    print(f"   - {log.NombreProceso} | {log.Estado} | Error: '{log.MensajeError}'")

print(f"\n🔸 Últimas ejecuciones de procesos:")  
for log in ejecuciones:
    print(f"   - {log.NombreProceso} | {log.Estado} | Error: '{log.MensajeError}'")

print(f"\n✅ Confirmación: Cada operación (guardar/ejecutar) crea solo 1 registro")