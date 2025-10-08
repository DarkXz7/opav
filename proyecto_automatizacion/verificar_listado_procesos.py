"""
Script para verificar la información de procesos en el listado
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'proyecto_automatizacion.settings')
django.setup()

from automatizacion.models import MigrationProcess
from automatizacion.logs.models_logs import ProcesoLog
from django.db.models import Q

print("=" * 80)
print("📋 VERIFICACIÓN DE LISTADO DE PROCESOS")
print("=" * 80)

processes = MigrationProcess.objects.all().order_by('-created_at')

print(f"\nTotal de procesos: {processes.count()}")
print("\n" + "=" * 80)

for i, process in enumerate(processes[:10], 1):  # Mostrar solo primeros 10
    print(f"\n{i}. PROCESO: {process.name}")
    print(f"   ID: {process.id}")
    print(f"   Tipo: {process.source.source_type}")
    print(f"   Creado: {process.created_at.strftime('%d/%m/%Y %H:%M')}")
    
    # Target info
    if process.selected_tables:
        print(f"   Tablas: {len(process.selected_tables)} -> {process.selected_tables[:2]}")
    elif process.selected_sheets:
        print(f"   Hojas: {len(process.selected_sheets)} -> {process.selected_sheets[:2]}")
    elif process.target_table:
        print(f"   Tabla destino: {process.target_table}")
    else:
        print(f"   Sin tablas/hojas configuradas")
    
    # Última ejecución
    if process.source.source_type == 'sql':
        last_log = ProcesoLog.objects.filter(
            Q(MigrationProcessID=process.id) | Q(NombreProceso=process.name)
        ).order_by('-FechaEjecucion').first()
        
        if last_log:
            print(f"   Última ejecución (SQL): {last_log.FechaEjecucion.strftime('%d/%m/%Y %H:%M')}")
            print(f"   Estado: {last_log.Estado}")
        else:
            print(f"   Última ejecución: Nunca ejecutado")
    else:
        last_log = process.logs.order_by('-timestamp').first()
        if last_log:
            print(f"   Última ejecución (Excel): {last_log.timestamp.strftime('%d/%m/%Y %H:%M')}")
            print(f"   Nivel: {last_log.level} - {last_log.stage}")
        else:
            print(f"   Última ejecución: Nunca ejecutado")
    
    print(f"   " + "-" * 70)

print("\n" + "=" * 80)
print("✅ Verificación completada")
print("=" * 80)
