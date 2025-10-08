"""
Script para encontrar el proceso "comida" y verificar su fecha
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'proyecto_automatizacion.settings')
django.setup()

from automatizacion.models import MigrationProcess
from django.utils import timezone

print("=" * 80)
print("🔍 BUSCANDO PROCESO 'comida'")
print("=" * 80)

# Buscar procesos que contengan "comida" en el nombre
processes = MigrationProcess.objects.filter(name__icontains='comida').order_by('-id')

print(f"\nProcesos encontrados con 'comida' en el nombre: {processes.count()}")

if processes.count() > 0:
    print("\n" + "=" * 80)
    for process in processes:
        print(f"\n📋 PROCESO: {process.name}")
        print(f"   ID: {process.id}")
        print(f"   created_at (raw): {process.created_at}")
        print(f"   created_at (formatted): {process.created_at.strftime('%d/%m/%Y %H:%M:%S')}")
        print(f"   Tipo: {process.source.source_type}")
        print(f"   Hace cuánto: {timezone.now() - process.created_at}")
        print(f"   Status: {process.status}")
else:
    print("\n❌ No se encontró ningún proceso con 'comida' en el nombre")
    print("\nBuscando en TODOS los procesos...")
    all_processes = MigrationProcess.objects.all().order_by('-id')[:10]
    print(f"\nÚltimos 10 procesos por ID:")
    for i, p in enumerate(all_processes, 1):
        print(f"   {i}. ID {p.id}: {p.name} - {p.created_at.strftime('%d/%m/%Y %H:%M:%S')}")

print("\n" + "=" * 80)
print(f"⏰ Hora actual UTC: {timezone.now().strftime('%d/%m/%Y %H:%M:%S')}")
print("=" * 80)
