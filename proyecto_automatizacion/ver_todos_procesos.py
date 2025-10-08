"""
Script para ver todos los procesos ordenados por ID
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'proyecto_automatizacion.settings')
django.setup()

from automatizacion.models import MigrationProcess

print("=" * 80)
print("📊 TODOS LOS PROCESOS ORDENADOS POR ID (DESCENDENTE)")
print("=" * 80)

processes = MigrationProcess.objects.all().order_by('-id')

print(f"\nTotal de procesos: {processes.count()}")
print(f"ID más alto: {processes.first().id if processes.exists() else 'N/A'}")
print(f"ID más bajo: {processes.last().id if processes.exists() else 'N/A'}")

print("\n" + "=" * 80)
print("TODOS LOS PROCESOS:")
print("=" * 80)

for i, process in enumerate(processes, 1):
    created_date = process.created_at.strftime('%d/%m/%Y %H:%M')
    print(f"{i:2}. ID {process.id:3} | {created_date} | {process.name[:40]:<40} | {process.source.source_type}")

print("=" * 80)
