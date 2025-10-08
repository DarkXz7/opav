"""
Script para verificar las fechas de creación de los procesos
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'proyecto_automatizacion.settings')
django.setup()

from automatizacion.models import MigrationProcess
from django.utils import timezone

print("=" * 80)
print("📅 VERIFICACIÓN DE FECHAS DE CREACIÓN")
print("=" * 80)
print(f"\nFecha/Hora actual del servidor: {timezone.now()}")
print(f"Timezone configurado: {timezone.get_current_timezone()}")

processes = MigrationProcess.objects.all().order_by('-created_at')[:10]

print(f"\nPrimeros 10 procesos ordenados por created_at DESC:")
print("=" * 80)

for i, process in enumerate(processes, 1):
    print(f"\n{i}. {process.name}")
    print(f"   ID: {process.id}")
    print(f"   created_at (raw): {process.created_at}")
    print(f"   created_at (formatted): {process.created_at.strftime('%d/%m/%Y %H:%M:%S')}")
    print(f"   Tipo de dato: {type(process.created_at)}")
    print(f"   Timezone aware: {timezone.is_aware(process.created_at)}")
    if timezone.is_aware(process.created_at):
        print(f"   Timezone: {process.created_at.tzinfo}")
        print(f"   UTC: {process.created_at.astimezone(timezone.utc)}")

print("\n" + "=" * 80)

# Verificar el proceso más reciente
latest = MigrationProcess.objects.latest('created_at')
print(f"\n🆕 PROCESO MÁS RECIENTE:")
print(f"   Nombre: {latest.name}")
print(f"   ID: {latest.id}")
print(f"   Fecha creación: {latest.created_at.strftime('%d/%m/%Y %H:%M:%S')}")
print(f"   Hace cuánto: {timezone.now() - latest.created_at}")

print("=" * 80)
