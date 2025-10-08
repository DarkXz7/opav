"""
Script para corregir procesos existentes con formato antiguo de columnas
Convierte: {"Hoja1": ["{'name': 'ID', ...}"]} 
A:         {"Hoja1": ["ID", "nombre", "edad"]}
"""

import os
import django
import json
import ast

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'proyecto_automatizacion.settings')
django.setup()

from automatizacion.models import MigrationProcess

def extract_column_name(column_str):
    """Extrae el nombre de la columna de un string con formato de diccionario"""
    try:
        # Si ya es un string simple, retornarlo
        if not column_str.startswith('{'):
            return column_str
            
        # Intentar parsear como diccionario
        column_dict = ast.literal_eval(column_str)
        if isinstance(column_dict, dict) and 'name' in column_dict:
            return column_dict['name']
        return column_str
    except:
        return column_str

def fix_process_columns(process):
    """Corrige las columnas de un proceso"""
    if not process.selected_columns:
        return False
        
    fixed = False
    new_columns = {}
    
    for sheet_name, columns in process.selected_columns.items():
        if not isinstance(columns, list):
            continue
            
        new_sheet_columns = []
        for col in columns:
            if isinstance(col, str) and '{' in col and 'name' in col:
                # Esta columna necesita corrección
                fixed_col = extract_column_name(col)
                new_sheet_columns.append(fixed_col)
                fixed = True
                print(f"  ❌ '{col[:50]}...' → ✅ '{fixed_col}'")
            else:
                new_sheet_columns.append(col)
        
        new_columns[sheet_name] = new_sheet_columns
    
    if fixed:
        process.selected_columns = new_columns
        process.save()
        print(f"✅ Proceso '{process.name}' (ID: {process.id}) corregido\n")
        return True
    else:
        print(f"ℹ️ Proceso '{process.name}' (ID: {process.id}) ya está correcto\n")
        return False

def main():
    print("=" * 70)
    print("🔧 CORRECCIÓN DE COLUMNAS EN PROCESOS EXISTENTES")
    print("=" * 70)
    
    processes = MigrationProcess.objects.filter(source__source_type='excel')
    
    if not processes.exists():
        print("ℹ️ No hay procesos Excel para corregir")
        return
    
    print(f"📋 Encontrados {processes.count()} procesos Excel\n")
    
    fixed_count = 0
    for process in processes:
        print(f"🔍 Revisando proceso: {process.name} (ID: {process.id})")
        
        if process.selected_columns:
            print(f"   Columnas actuales: {process.selected_columns}")
            if fix_process_columns(process):
                fixed_count += 1
                print(f"   Columnas corregidas: {process.selected_columns}")
        else:
            print(f"   ⚠️ No tiene columnas seleccionadas\n")
    
    print("=" * 70)
    print(f"✅ RESUMEN:")
    print(f"   Total procesos revisados: {processes.count()}")
    print(f"   Procesos corregidos: {fixed_count}")
    print(f"   Procesos sin cambios: {processes.count() - fixed_count}")
    print("=" * 70)

if __name__ == '__main__':
    main()
