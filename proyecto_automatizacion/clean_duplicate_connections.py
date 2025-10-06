#!/usr/bin/env python
"""
Script para limpiar conexiones duplicadas antes de aplicar la restricción unique
"""
import os
import sys
import django

# Configurar Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'proyecto_automatizacion.settings')
django.setup()

from automatizacion.models import DatabaseConnection
from django.db import transaction

def clean_duplicate_connections():
    """
    Elimina conexiones duplicadas, manteniendo solo la más reciente de cada nombre
    """
    print("Iniciando limpieza de conexiones duplicadas...")
    
    # Obtener todos los nombres únicos
    unique_names = DatabaseConnection.objects.values_list('name', flat=True).distinct()
    
    total_deleted = 0
    
    for name in unique_names:
        # Obtener todas las conexiones con este nombre
        connections = DatabaseConnection.objects.filter(name=name).order_by('-created_at')
        
        if connections.count() > 1:
            # Mantener la más reciente (la primera en el orden descendente)
            connections_to_delete = connections[1:]  # Todas excepto la primera
            
            print(f"Nombre '{name}': {connections.count()} conexiones encontradas")
            print(f"  - Manteniendo: ID {connections[0].id} (creada: {connections[0].created_at})")
            
            for conn in connections_to_delete:
                print(f"  - Eliminando: ID {conn.id} (creada: {conn.created_at})")
                conn.delete()
                total_deleted += 1
    
    print(f"\nLimpieza completada: {total_deleted} conexiones duplicadas eliminadas")
    print(f"Conexiones restantes: {DatabaseConnection.objects.count()}")

if __name__ == '__main__':
    with transaction.atomic():
        clean_duplicate_connections()