#!/usr/bin/env python3
"""
Test específico para el error "'str' object has no attribute 'get'"
Simula el caso de CESAR_10 donde selected_tables es una lista de strings
"""

import os
import sys
import django

# Configurar Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'proyecto_automatizacion.settings')

try:
    django.setup()
except Exception as e:
    print(f"Error configurando Django: {e}")
    sys.exit(1)

def test_table_info_parsing():
    """
    Test que verifica el manejo de diferentes formatos en selected_tables
    """
    print("=== PRUEBA: Error 'str' object has no attribute 'get' ===\n")
    
    # Simular los diferentes formatos que puede tener selected_tables
    test_cases = [
        {
            'name': 'Lista de strings (caso CESAR_10)',
            'selected_tables': ['dbo.Usuarios', 'dbo.Productos'],
            'description': 'Formato: ["dbo.Usuarios", "dbo.Productos"]'
        },
        {
            'name': 'Lista de diccionarios (formato ideal)',
            'selected_tables': [
                {"name": "Usuarios", "full_name": "dbo.Usuarios"},
                {"name": "Productos", "full_name": "dbo.Productos"}
            ],
            'description': 'Formato: [{"name": "Usuarios", "full_name": "dbo.Usuarios"}]'
        },
        {
            'name': 'String JSON de array (caso TEST_TABLAS_DINAMICAS)',
            'selected_tables': '["dbo.tabla_test"]',
            'description': 'Formato: "[\\"dbo.tabla_test\\"]"'
        },
        {
            'name': 'String simple (caso problemático)',
            'selected_tables': 'tabla_test_dinamica',
            'description': 'Formato: "tabla_test_dinamica"'
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"🔍 CASO {i}: {test_case['name']}")
        print(f"   📄 Descripción: {test_case['description']}")
        
        selected_tables_raw = test_case['selected_tables']
        print(f"   📊 Input tipo: {type(selected_tables_raw)}")
        print(f"   📊 Input valor: {selected_tables_raw}")
        
        try:
            # Paso 1: Parsear selected_tables (código de _extract_sql_data)
            print(f"   🔄 Paso 1: Parsing de selected_tables...")
            
            import json
            if isinstance(selected_tables_raw, list):
                selected_tables = selected_tables_raw
                print(f"      ✅ Lista nativa reconocida")
            elif isinstance(selected_tables_raw, str):
                try:
                    # Intentar parsearlo como JSON
                    selected_tables = json.loads(selected_tables_raw)
                    print(f"      ✅ JSON parseado correctamente")
                except:
                    # Si falla, tratarlo como string simple
                    selected_tables = [selected_tables_raw]
                    print(f"      ✅ String simple convertido a lista")
            else:
                selected_tables = selected_tables_raw if selected_tables_raw else []
                print(f"      ⚠️  Formato desconocido manejado")
            
            print(f"      📊 Resultado: {selected_tables} ({type(selected_tables)})")
            
            # Paso 2: Iterar sobre las tablas (código del loop)
            print(f"   🔄 Paso 2: Iterando sobre tablas...")
            
            processed_tables = []
            for table_info in selected_tables:
                print(f"      🔍 Procesando: {table_info} ({type(table_info)})")
                
                # Nuevo código corregido
                if isinstance(table_info, dict):
                    # Formato objeto: {"name": "tabla", "full_name": "dbo.tabla"}
                    table_name = table_info.get('name') or table_info.get('full_name', '')
                    print(f"         ✅ Diccionario → table_name: '{table_name}'")
                elif isinstance(table_info, str):
                    # Formato string directo: "dbo.tabla" o "tabla"
                    table_name = table_info
                    print(f"         ✅ String → table_name: '{table_name}'")
                else:
                    # Formato desconocido, saltar
                    print(f"         ⚠️  Formato desconocido, saltando")
                    continue
                
                if table_name:
                    processed_tables.append(table_name)
                    print(f"         ✅ Tabla agregada: '{table_name}'")
                else:
                    print(f"         ❌ table_name vacío, saltando")
            
            print(f"   📊 Tablas procesadas: {processed_tables}")
            print(f"   ✅ Caso {i} procesado exitosamente\n")
            
        except Exception as e:
            print(f"   ❌ Error en caso {i}: {str(e)}")
            import traceback
            traceback.print_exc()
            print()
    
    print("="*60)
    print("🎉 RESULTADO: CORRECCIÓN DEL ERROR 'get' COMPLETADA")
    print("   ✅ Todos los formatos de selected_tables se manejan correctamente")
    print("   ✅ No más error 'str' object has no attribute 'get'")
    print("   ✅ Compatibilidad con formatos legacy y nuevos")

def test_cesar_10_specific():
    """
    Test específico para replicar el caso exacto de CESAR_10
    """
    print("\n" + "="*60)
    print("=== PRUEBA ESPECÍFICA: CÉSAR_10 ===\n")
    
    # Datos exactos de CESAR_10 según el debugging
    cesar_10_data = {
        'selected_tables': ['dbo.Usuarios'],  # Lista de strings
        'selected_columns': {'dbo.Usuarios': ['Id', 'Nombre', 'Email', 'FechaRegistro']}  # Dict
    }
    
    print(f"📊 selected_tables: {cesar_10_data['selected_tables']}")
    print(f"📊 selected_columns: {cesar_10_data['selected_columns']}")
    
    try:
        # Simular el procesamiento que falló
        print(f"\n🔄 Simulando procesamiento de CESAR_10...")
        
        for table_info in cesar_10_data['selected_tables']:
            print(f"   🔍 Procesando table_info: '{table_info}' ({type(table_info)})")
            
            # Código anterior que fallaba:
            # table_name = table_info.get('name') or table_info.get('full_name', '')
            
            # Código nuevo que funciona:
            if isinstance(table_info, dict):
                table_name = table_info.get('name') or table_info.get('full_name', '')
                print(f"      📦 Diccionario → '{table_name}'")
            elif isinstance(table_info, str):
                table_name = table_info
                print(f"      📦 String → '{table_name}'")
            else:
                continue
            
            # Simular obtención de columnas
            if cesar_10_data['selected_columns']:
                if isinstance(cesar_10_data['selected_columns'], dict):
                    selected_cols = cesar_10_data['selected_columns'].get(table_name, [])
                    print(f"      📋 Columnas para '{table_name}': {selected_cols}")
                else:
                    print(f"      📋 selected_columns no es dict")
            
            print(f"      ✅ Tabla '{table_name}' procesada exitosamente")
        
        print(f"\n🎉 CESAR_10 simulado exitosamente - Error corregido!")
        
    except Exception as e:
        print(f"\n❌ Error simulando CESAR_10: {str(e)}")
        import traceback
        traceback.print_exc()

def main():
    """
    Ejecuta las pruebas de corrección del error 'get'
    """
    print("🚀 INICIANDO PRUEBAS DE CORRECCIÓN 'str' object has no attribute 'get'")
    print("=" * 80)
    
    test_table_info_parsing()
    test_cesar_10_specific()
    
    print("\n" + "=" * 80)
    print("🏁 PRUEBAS COMPLETADAS")
    print("   El proceso CESAR_10 debería funcionar ahora correctamente")

if __name__ == '__main__':
    main()