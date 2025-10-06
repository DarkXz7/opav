#!/usr/bin/env python
"""
Script para limpiar procesos duplicados antes de aplicar la restricción unique
"""
import os
import sys
import django

# Configurar Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'proyecto_automatizacion.settings')
django.setup()

from automatizacion.models import MigrationProcess
from django.db import transaction

def clean_duplicate_processes():
    """
    Elimina procesos duplicados, manteniendo solo el más reciente de cada nombre
    """
    print("Iniciando limpieza de procesos duplicados...")
    
    # Obtener todos los nombres únicos
    unique_names = MigrationProcess.objects.values_list('name', flat=True).distinct()
    
    total_deleted = 0
    
    for name in unique_names:
        # Obtener todos los procesos con este nombre
        processes = MigrationProcess.objects.filter(name=name).order_by('-created_at')
        
        if processes.count() > 1:
            # Mantener el más reciente (el primero en el orden descendente)
            processes_to_delete = processes[1:]  # Todos excepto el primero
            
            print(f"Nombre '{name}': {processes.count()} procesos encontrados")
            print(f"  - Manteniendo: ID {processes[0].id} (creado: {processes[0].created_at})")
            
            for proc in processes_to_delete:
                print(f"  - Eliminando: ID {proc.id} (creado: {proc.created_at})")
                proc.delete()
                total_deleted += 1
    
    print(f"\nLimpieza completada: {total_deleted} procesos duplicados eliminados")
    print(f"Procesos restantes: {MigrationProcess.objects.count()}")

if __name__ == '__main__':
    with transaction.atomic():
        clean_duplicate_processes()