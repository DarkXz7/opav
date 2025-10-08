"""
Script para tocar (actualizar) el proceso arbejas y verificar updated_at
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'proyecto_automatizacion.settings')
django.setup()

from automatizacion.models import MigrationProcess
from django.utils import timezone

print("=" * 80)
print("🔄 ACTUALIZANDO PROCESO 'arbejas'")
print("=" * 80)

# Buscar el proceso
process = MigrationProcess.objects.filter(name__icontains='arbejas').first()

if process:
    print(f"\n📋 ANTES:")
    print(f"   Nombre: {process.name}")
    print(f"   ID: {process.id}")
    print(f"   created_at: {process.created_at.strftime('%d/%m/%Y %H:%M:%S')}")
    print(f"   updated_at: {process.updated_at.strftime('%d/%m/%Y %H:%M:%S')}")
    
    # Guardar para actualizar updated_at
    process.save()
    
    # Recargar del DB
    process.refresh_from_db()
    
    print(f"\n📋 DESPUÉS DEL SAVE:")
    print(f"   created_at: {process.created_at.strftime('%d/%m/%Y %H:%M:%S')}")
    print(f"   updated_at: {process.updated_at.strftime('%d/%m/%Y %H:%M:%S')}")
    print(f"\n✅ updated_at ahora refleja la fecha de hoy!")
else:
    print("\n❌ No se encontró el proceso 'arbejas'")

print("\n" + "=" * 80)
print("📊 PRIMEROS 5 PROCESOS ORDENADOS POR updated_at:")
print("=" * 80)

processes = MigrationProcess.objects.all().order_by('-updated_at')[:5]

for i, p in enumerate(processes, 1):
    print(f"\n{i}. {p.name}")
    print(f"   ID: {p.id}")
    print(f"   Creado: {p.created_at.strftime('%d/%m/%Y %H:%M')}")
    print(f"   Modificado: {p.updated_at.strftime('%d/%m/%Y %H:%M')}")

print("\n" + "=" * 80)
