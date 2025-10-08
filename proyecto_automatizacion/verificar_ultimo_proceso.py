"""
Script para verificar el proceso más reciente creado
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'proyecto_automatizacion.settings')
django.setup()

from automatizacion.models import MigrationProcess
from django.utils import timezone
from datetime import datetime

print("=" * 80)
print("🆕 PROCESO MÁS RECIENTE")
print("=" * 80)

# Obtener el proceso más reciente
latest = MigrationProcess.objects.latest('id')  # Por ID (auto-increment)
latest_by_date = MigrationProcess.objects.latest('created_at')  # Por fecha

print(f"\n📋 POR ID (el último insertado):")
print(f"   ID: {latest.id}")
print(f"   Nombre: {latest.name}")
print(f"   Fecha creación (raw): {latest.created_at}")
print(f"   Fecha creación (formatted): {latest.created_at.strftime('%d/%m/%Y %H:%M:%S')}")
print(f"   Tipo: {latest.source.source_type}")

print(f"\n📋 POR FECHA (el más reciente por created_at):")
print(f"   ID: {latest_by_date.id}")
print(f"   Nombre: {latest_by_date.name}")
print(f"   Fecha creación (raw): {latest_by_date.created_at}")
print(f"   Fecha creación (formatted): {latest_by_date.created_at.strftime('%d/%m/%Y %H:%M:%S')}")
print(f"   Tipo: {latest_by_date.source.source_type}")

if latest.id != latest_by_date.id:
    print("\n⚠️ ADVERTENCIA: El proceso con mayor ID NO es el mismo que el más reciente por fecha")
else:
    print("\n✅ OK: El proceso con mayor ID coincide con el más reciente por fecha")

# Mostrar los últimos 5 procesos
print(f"\n📊 ÚLTIMOS 5 PROCESOS CREADOS:")
print("=" * 80)

processes = MigrationProcess.objects.all().order_by('-created_at')[:5]

for i, process in enumerate(processes, 1):
    created_date = process.created_at.strftime('%d/%m/%Y %H:%M:%S')
    print(f"{i}. ID {process.id}: {process.name}")
    print(f"   Fecha: {created_date}")
    print(f"   Hace: {timezone.now() - process.created_at}")
    print()

print("=" * 80)
print(f"\n⏰ Hora actual del sistema: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
print(f"⏰ Hora actual UTC: {timezone.now().strftime('%d/%m/%Y %H:%M:%S')}")
print("=" * 80)
