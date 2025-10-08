"""
Script para buscar el proceso 'arbejas' recién creado
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'proyecto_automatizacion.settings')
django.setup()

from automatizacion.models import MigrationProcess
from django.utils import timezone
import pytz

print("=" * 80)
print("🔍 BUSCANDO PROCESO 'arbejas'")
print("=" * 80)

# Buscar el proceso arbejas
processes = MigrationProcess.objects.filter(name__icontains='arbejas').order_by('-id')

print(f"\nProcesos encontrados: {processes.count()}")

if processes.count() > 0:
    for process in processes:
        print(f"\n📋 PROCESO: {process.name}")
        print(f"   ID: {process.id}")
        print(f"   created_at (RAW desde DB): {process.created_at}")
        print(f"   created_at (str): {str(process.created_at)}")
        print(f"   created_at (repr): {repr(process.created_at)}")
        print(f"   Timezone info: {process.created_at.tzinfo}")
        print(f"   Is aware: {timezone.is_aware(process.created_at)}")
        
        # Mostrar en diferentes formatos
        print(f"\n   📅 FORMATOS DE FECHA:")
        print(f"   Formato ISO: {process.created_at.isoformat()}")
        print(f"   Formato d/m/Y: {process.created_at.strftime('%d/%m/%Y')}")
        print(f"   Formato Y-m-d: {process.created_at.strftime('%Y-%m-%d')}")
        print(f"   Formato completo: {process.created_at.strftime('%d/%m/%Y %H:%M:%S %Z')}")
        
        # Convertir a hora local
        print(f"\n   🌍 CONVERSIONES DE TIMEZONE:")
        print(f"   UTC: {process.created_at}")
        
        # Intentar convertir a timezone local
        try:
            local_tz = pytz.timezone('America/Bogota')  # Ajusta según tu zona
            local_time = process.created_at.astimezone(local_tz)
            print(f"   Local (Bogotá): {local_time.strftime('%d/%m/%Y %H:%M:%S')}")
        except:
            pass
            
        print(f"\n   Tipo: {process.source.source_type}")
        print(f"   Status: {process.status}")

# Verificar también el proceso con ID más alto
print("\n" + "=" * 80)
print("PROCESO CON ID MÁS ALTO:")
print("=" * 80)

latest_by_id = MigrationProcess.objects.all().order_by('-id').first()
if latest_by_id:
    print(f"\nID: {latest_by_id.id}")
    print(f"Nombre: {latest_by_id.name}")
    print(f"created_at: {latest_by_id.created_at}")
    print(f"Fecha: {latest_by_id.created_at.strftime('%d/%m/%Y %H:%M:%S')}")

print("\n" + "=" * 80)
print(f"⏰ Hora actual del sistema (Python datetime.now()):")
from datetime import datetime
print(f"   {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
print(f"\n⏰ Hora actual UTC (Django timezone.now()):")
print(f"   {timezone.now().strftime('%d/%m/%Y %H:%M:%S')}")
print("=" * 80)
