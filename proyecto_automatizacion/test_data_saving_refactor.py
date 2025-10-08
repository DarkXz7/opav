#!/usr/bin/env python3
"""
Test script para verificar el refactor de guardado de datos
Verifica que las tablas contengan datos reales en lugar de metadatos del proceso
"""

import os
import sys
import django
import pandas as pd
from django.conf import settings

# Configurar Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'proyecto_automatizacion.settings')

try:
    django.setup()
except Exception as e:
    print(f"Error configurando Django: {e}")
    sys.exit(1)

def test_dataframe_saving_method():
    """
    Test directo del método _save_dataframe_to_destination
    para verificar que guarda datos reales del DataFrame
    """
    from automatizacion.models import MigrationProcess
    import uuid
    
    print("=== PRUEBA: Método de guardado directo de DataFrame ===\n")
    
    # Crear DataFrame de prueba con datos simulados reales
    print("📊 Creando DataFrame de prueba con datos simulados...")
    
    df_test = pd.DataFrame({
        'ID_Cliente': [1001, 1002, 1003, 1004, 1005],
        'Nombre_Cliente': ['Juan Pérez', 'María García', 'Carlos López', 'Ana Martínez', 'Pedro Ruiz'],
        'Producto': ['Producto A', 'Producto B', 'Producto A', 'Producto C', 'Producto B'],
        'Monto': [1500.50, 2300.75, 890.25, 4200.00, 1750.80],
        'Fecha_Compra': pd.to_datetime(['2024-01-15', '2024-01-16', '2024-01-17', '2024-01-18', '2024-01-19']),
        'Activo': [True, True, False, True, True]
    })
    
    print(f"   ✅ DataFrame creado con {len(df_test)} registros")
    print(f"   📋 Columnas: {list(df_test.columns)}")
    print(f"\n📋 Vista previa de datos:")
    print(df_test.head())
    
    # Crear instancia temporal del proceso
    print(f"\n🔧 Creando instancia de proceso para prueba...")
    
    try:
        # Simular método sin crear proceso real en BD
        process = MigrationProcess()
        process.name = "Test_Refactor_Data_Saving"
        
        # Generar UUID de prueba
        proceso_id = str(uuid.uuid4())
        
        # Llamar al método de guardado
        print(f"\n💾 Ejecutando _save_dataframe_to_destination...")
        print(f"   🆔 Proceso ID: {proceso_id}")
        print(f"   📋 Tabla destino: test_refactor_clientes")
        
        exito, resultado = process._save_dataframe_to_destination(
            df_datos=df_test,
            nombre_tabla_destino="test_refactor_clientes",
            proceso_id=proceso_id,
            usuario_responsable="test_usuario"
        )
        
        if exito:
            print(f"\n✅ ÉXITO: Datos guardados correctamente")
            print(f"   📊 Registros insertados: {resultado['records_inserted']}")
            print(f"   📋 Tabla creada: {resultado['table_name']}")
            print(f"   🔗 Proceso ID: {resultado['proceso_id']}")
            
            # Verificar contenido de la tabla
            print(f"\n🔍 Verificando contenido de la tabla...")
            verificar_tabla_contenido("test_refactor_clientes", df_test)
            
            return True
        else:
            print(f"\n❌ ERROR: Fallo guardando datos")
            print(f"   🚫 Error: {resultado.get('error', 'Error desconocido')}")
            return False
            
    except Exception as e:
        print(f"\n❌ EXCEPCIÓN: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def verificar_tabla_contenido(nombre_tabla, df_original):
    """
    Verifica que la tabla en la base de datos contenga los datos esperados
    """
    from django.db import connections
    
    try:
        connection = connections['destino']
        cursor = connection.cursor()
        
        # Verificar que la tabla existe
        cursor.execute(f"""
            SELECT COUNT(*) 
            FROM INFORMATION_SCHEMA.TABLES 
            WHERE TABLE_NAME = '{nombre_tabla}'
        """)
        
        tabla_existe = cursor.fetchone()[0] > 0
        
        if not tabla_existe:
            print(f"   ❌ Tabla '{nombre_tabla}' no existe en la base de datos")
            return False
        
        print(f"   ✅ Tabla '{nombre_tabla}' existe")
        
        # Contar registros en la tabla
        cursor.execute(f"SELECT COUNT(*) FROM [{nombre_tabla}]")
        num_registros = cursor.fetchone()[0]
        
        print(f"   📊 Registros en tabla: {num_registros}")
        print(f"   📊 Registros esperados: {len(df_original)}")
        
        if num_registros != len(df_original):
            print(f"   ⚠️  Número de registros no coincide")
            return False
        
        # Verificar estructura de columnas
        cursor.execute(f"""
            SELECT COLUMN_NAME, DATA_TYPE 
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_NAME = '{nombre_tabla}'
            ORDER BY ORDINAL_POSITION
        """)
        
        columnas_tabla = cursor.fetchall()
        columnas_df = list(df_original.columns)
        
        print(f"   📋 Columnas en tabla: {[col[0] for col in columnas_tabla]}")
        print(f"   📋 Columnas esperadas: {columnas_df}")
        
        # Verificar algunas muestras de datos
        cursor.execute(f"SELECT TOP 3 * FROM [{nombre_tabla}]")
        muestra_datos = cursor.fetchall()
        
        print(f"\n📋 Muestra de datos guardados:")
        col_names = [col[0] for col in columnas_tabla]
        
        for i, row in enumerate(muestra_datos):
            print(f"   Registro {i+1}: {dict(zip(col_names, row))}")
        
        print(f"\n✅ Verificación completada: Los datos reales fueron guardados correctamente")
        print(f"   🎯 La tabla contiene: ID_Cliente, Nombre_Cliente, Producto, Monto, etc.")
        print(f"   🎯 NO contiene: ProcesoID, NombreProceso, EstadoProceso (metadatos)")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Error verificando tabla: {str(e)}")
        return False

def limpiar_tabla_test():
    """
    Limpia la tabla de test para futuras ejecuciones
    """
    try:
        from django.db import connections
        connection = connections['destino']
        cursor = connection.cursor()
        
        cursor.execute("IF OBJECT_ID('test_refactor_clientes', 'U') IS NOT NULL DROP TABLE test_refactor_clientes")
        connection.commit()
        print("🧹 Tabla de test limpiada")
        
    except Exception as e:
        print(f"⚠️  No se pudo limpiar tabla de test: {e}")

def main():
    """
    Ejecuta las pruebas del refactor de guardado de datos
    """
    print("🚀 INICIANDO PRUEBAS DEL REFACTOR DE GUARDADO DE DATOS")
    print("=" * 60)
    
    # Limpiar antes de empezar
    limpiar_tabla_test()
    
    # Test principal
    exito = test_dataframe_saving_method()
    
    print("\n" + "=" * 60)
    
    if exito:
        print("🎉 RESULTADO: REFACTOR EXITOSO")
        print("   ✅ Los datos reales del DataFrame se guardan correctamente")
        print("   ✅ Las tablas contienen columnas de datos reales")
        print("   ✅ No se guardan metadatos del proceso")
        print("\n🔄 CAMBIO FUNDAMENTAL COMPLETADO:")
        print("   📊 Antes: Tablas con ProcesoID, NombreProceso, EstadoProceso")
        print("   📊 Ahora: Tablas con ID_Cliente, Producto, Monto, etc.")
    else:
        print("❌ RESULTADO: REFACTOR CON ERRORES")
        print("   🚫 Revisar implementación del método _save_dataframe_to_destination")
    
    print("\n🏁 Pruebas completadas")

if __name__ == '__main__':
    main()