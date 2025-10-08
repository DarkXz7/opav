"""
Script para verificar los valores del campo Estado en ProcesoLog
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'proyecto_automatizacion.settings')
django.setup()

from automatizacion.logs.models_logs import ProcesoLog

# Ver todos los valores únicos de Estado
estados = ProcesoLog.objects.values_list('Estado', flat=True).distinct()

print("=" * 70)
print("📊 VALORES ÚNICOS DEL CAMPO 'Estado' EN ProcesoLog")
print("=" * 70)

for estado in estados:
    count = ProcesoLog.objects.filter(Estado=estado).count()
    print(f"   '{estado}': {count} registros")

print("\n" + "=" * 70)
print("📋 ÚLTIMOS 10 LOGS:")
print("=" * 70)

logs = ProcesoLog.objects.all().order_by('-FechaEjecucion')[:10]

for log in logs:
    error_indicator = "❌" if log.MensajeError else "✅"
    print(f"\n{error_indicator} ProcesoID: {log.ProcesoID[:8]}...")
    print(f"   Nombre: {log.NombreProceso}")
    print(f"   Estado: '{log.Estado}'")
    print(f"   MigrationProcessID: {log.MigrationProcessID}")
    print(f"   Fecha: {log.FechaEjecucion}")
    print(f"   MensajeError: {log.MensajeError[:100] if log.MensajeError else 'None'}")

print("\n" + "=" * 70)
