"""
Script de prueba para la nueva funcionalidad de edición completa de campos
Verifica que se carguen todos los campos originales del Excel en la vista de edición
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'proyecto_automatizacion.settings')
django.setup()

from automatizacion.models import MigrationProcess
from automatizacion.utils import ExcelProcessor

def test_edit_view_data():
    """Prueba que la vista de edición tenga todos los datos necesarios"""
    
    print("=" * 70)
    print("🧪 PRUEBA: Datos para Vista de Edición de Procesos Excel")
    print("=" * 70)
    
    # Buscar un proceso Excel
    processes = MigrationProcess.objects.filter(source__source_type='excel').order_by('-id')
    
    if not processes.exists():
        print("❌ No hay procesos Excel para probar")
        return
    
    process = processes.first()
    print(f"\n📋 Proceso de prueba: {process.name} (ID: {process.id})")
    print(f"   Archivo: {process.source.file_path}")
    
    # Simular lo que hace la vista edit_process
    try:
        processor = ExcelProcessor(process.source.file_path)
        available_sheets = processor.get_sheet_names()
        
        print(f"\n📊 Hojas disponibles: {available_sheets}")
        
        # Cargar todos los datos de las hojas (como en la vista)
        all_sheets_data = {}
        for sheet_name in available_sheets:
            columns = processor.get_sheet_columns(sheet_name)
            preview = processor.get_sheet_preview(sheet_name)
            
            all_sheets_data[sheet_name] = {
                'columns': columns,
                'preview': preview,
                'total_rows': preview.get('total_rows', 0) if preview else 0,
                'column_count': len(columns) if columns else 0
            }
        
        # Mostrar información detallada
        for sheet_name, sheet_data in all_sheets_data.items():
            print(f"\n📄 Hoja: {sheet_name}")
            print(f"   Total de campos originales: {sheet_data['column_count']}")
            print(f"   Total de registros: {sheet_data['total_rows']}")
            
            # Obtener campos seleccionados actualmente en el proceso
            selected_cols = []
            if process.selected_columns and sheet_name in process.selected_columns:
                selected_cols = process.selected_columns[sheet_name]
            
            print(f"   Campos seleccionados en proceso: {len(selected_cols)}")
            
            # Mostrar todos los campos con su estado
            print(f"\n   📋 Listado de campos:")
            for col in sheet_data['columns']:
                is_selected = col['name'] in selected_cols if selected_cols else False
                status = "✅ ACTIVO  " if is_selected else "⚪ DISPONIBLE"
                print(f"      {status} | {col['name']:<20} | {col['sql_type']}")
            
            # Verificar que hay campos disponibles para reactivar
            available_to_activate = [
                col['name'] for col in sheet_data['columns'] 
                if col['name'] not in selected_cols
            ]
            
            if available_to_activate:
                print(f"\n   💡 Campos disponibles para reactivar ({len(available_to_activate)}):")
                for col_name in available_to_activate[:5]:  # Mostrar máximo 5
                    print(f"      - {col_name}")
                if len(available_to_activate) > 5:
                    print(f"      ... y {len(available_to_activate) - 5} más")
            else:
                print(f"\n   ℹ️ Todos los campos están activos")
        
        print("\n" + "=" * 70)
        print("✅ PRUEBA EXITOSA: Los datos se cargan correctamente")
        print("=" * 70)
        print(f"\n🌐 Puedes probar en:")
        print(f"   http://127.0.0.1:8000/automatizacion/process/{process.id}/edit/")
        print("=" * 70)
        
    except Exception as e:
        print(f"\n❌ Error al procesar: {str(e)}")
        import traceback
        traceback.print_exc()

def test_column_reactivation_scenario():
    """Prueba el escenario de reactivación de campos"""
    
    print("\n" + "=" * 70)
    print("🧪 PRUEBA: Escenario de Reactivación de Campos")
    print("=" * 70)
    
    processes = MigrationProcess.objects.filter(
        source__source_type='excel',
        selected_columns__isnull=False
    ).order_by('-id')
    
    if not processes.exists():
        print("❌ No hay procesos Excel con columnas seleccionadas")
        return
    
    for process in processes[:3]:  # Probar los 3 más recientes
        print(f"\n📋 Proceso: {process.name} (ID: {process.id})")
        
        try:
            processor = ExcelProcessor(process.source.file_path)
            
            for sheet_name in process.selected_sheets or []:
                all_columns = processor.get_sheet_columns(sheet_name)
                selected_columns = process.selected_columns.get(sheet_name, [])
                
                all_col_names = [col['name'] for col in all_columns]
                inactive_cols = [col for col in all_col_names if col not in selected_columns]
                
                print(f"\n   📄 Hoja: {sheet_name}")
                print(f"      Total campos originales: {len(all_col_names)}")
                print(f"      Campos activos: {len(selected_columns)}")
                print(f"      Campos inactivos (pueden reactivarse): {len(inactive_cols)}")
                
                if inactive_cols:
                    print(f"      🔄 Campos que puedes reactivar:")
                    for col in inactive_cols[:3]:
                        print(f"         - {col}")
                    if len(inactive_cols) > 3:
                        print(f"         ... y {len(inactive_cols) - 3} más")
        
        except Exception as e:
            print(f"      ⚠️ Error: {str(e)}")
    
    print("\n" + "=" * 70)

if __name__ == '__main__':
    test_edit_view_data()
    test_column_reactivation_scenario()
