"""
Script de prueba para verificar la normalización de valores vacíos según tipo SQL.

Simula el comportamiento completo del sistema:
1. normalize_df_for_sql() - convierte inválidos a None
2. apply_default_values_from_mappings() - aplica defaults según config
3. Verifica que los resultados sean correctos
"""
import sys
import os
import pandas as pd
import numpy as np

# Agregar el directorio del proyecto al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from automatizacion.sql_utils import normalize_df_for_sql, apply_default_values_from_mappings


def print_separator(title):
    print("\n" + "="*80)
    print(f"  {title}")
    print("="*80)


def test_int_column_not_nullable():
    """Test: Columna INT con nullable=False y default=0"""
    print_separator("TEST 1: Columna INT con nullable=False y default=0")
    
    # Datos de prueba
    df = pd.DataFrame({
        'cantidad': [5, None, '', 10, np.nan, 'abc']
    })
    
    print("📊 Datos originales:")
    print(df)
    print(f"\nTipos: {df.dtypes}")
    
    # Paso 1: Normalizar (convierte inválidos a None)
    df_normalized, issues = normalize_df_for_sql(df, strict=False)
    print("\n✅ Después de normalize_df_for_sql():")
    print(df_normalized)
    print(f"Issues: {issues}")
    
    # Paso 2: Aplicar defaults
    column_mappings = {
        'cantidad': {
            'sql_type': 'INT',
            'nullable': False,
            'default_value': '0'
        }
    }
    
    df_final = apply_default_values_from_mappings(df_normalized, column_mappings)
    print("\n🎯 Después de apply_default_values_from_mappings():")
    print(df_final)
    
    # Verificación
    expected = [5.0, 0, 0, 10.0, 0, 0]  # Todos los None deben ser 0
    actual = df_final['cantidad'].tolist()
    
    print(f"\n🔍 Verificación:")
    print(f"   Esperado: {expected}")
    print(f"   Obtenido: {actual}")
    
    if actual == expected:
        print("   ✅ TEST PASADO")
    else:
        print("   ❌ TEST FALLADO")
    
    return actual == expected


def test_int_column_nullable():
    """Test: Columna INT con nullable=True (debe mantener None)"""
    print_separator("TEST 2: Columna INT con nullable=True")
    
    df = pd.DataFrame({
        'cantidad': [5, None, '', 10, np.nan]
    })
    
    print("📊 Datos originales:")
    print(df)
    
    # Normalizar
    df_normalized, _ = normalize_df_for_sql(df, strict=False)
    
    # Aplicar defaults (nullable=True no debe cambiar None)
    column_mappings = {
        'cantidad': {
            'sql_type': 'INT',
            'nullable': True,
            'default_value': '0'
        }
    }
    
    df_final = apply_default_values_from_mappings(df_normalized, column_mappings)
    print("\n🎯 Resultado final:")
    print(df_final)
    
    # Verificar que los None se mantienen
    none_count = df_final['cantidad'].isna().sum()
    print(f"\n🔍 Cantidad de None: {none_count}")
    
    if none_count > 0:
        print("   ✅ TEST PASADO (None se mantienen con nullable=True)")
        return True
    else:
        print("   ❌ TEST FALLADO (None fueron reemplazados incorrectamente)")
        return False


def test_date_column_getdate():
    """Test: Columna DATE con nullable=False y default=GETDATE()"""
    print_separator("TEST 3: Columna DATE con nullable=False y default=GETDATE()")
    
    df = pd.DataFrame({
        'fecha': ['2024-01-15', None, '', '2024-01-17', np.nan]
    })
    
    print("📊 Datos originales:")
    print(df)
    
    # Normalizar
    df_normalized, _ = normalize_df_for_sql(df, strict=False)
    print("\n✅ Después de normalizar:")
    print(df_normalized)
    
    # Aplicar defaults
    column_mappings = {
        'fecha': {
            'sql_type': 'DATE',
            'nullable': False,
            'default_value': 'GETDATE()'
        }
    }
    
    df_final = apply_default_values_from_mappings(df_normalized, column_mappings)
    print("\n🎯 Resultado final:")
    print(df_final)
    print(f"\nTipos: {df_final.dtypes}")
    
    # Verificar que los None fueron reemplazados con timestamp
    none_count = df_final['fecha'].isna().sum()
    timestamp_count = df_final['fecha'].apply(lambda x: isinstance(x, pd.Timestamp)).sum()
    
    print(f"\n🔍 Verificación:")
    print(f"   None restantes: {none_count}")
    print(f"   Timestamps: {timestamp_count}")
    
    if none_count == 0 and timestamp_count == 5:
        print("   ✅ TEST PASADO")
        return True
    else:
        print("   ❌ TEST FALLADO")
        return False


def test_varchar_column():
    """Test: Columna VARCHAR con nullable=False y default='' """
    print_separator("TEST 4: Columna VARCHAR con nullable=False y default=''")
    
    df = pd.DataFrame({
        'nombre': ['Juan', None, '', 'Pedro', np.nan, '  ']
    })
    
    print("📊 Datos originales:")
    print(df)
    
    # Normalizar
    df_normalized, _ = normalize_df_for_sql(df, strict=False)
    print("\n✅ Después de normalizar:")
    print(df_normalized)
    
    # Aplicar defaults
    column_mappings = {
        'nombre': {
            'sql_type': 'NVARCHAR(255)',
            'nullable': False,
            'default_value': None  # Sin default explícito, debe usar ''
        }
    }
    
    df_final = apply_default_values_from_mappings(df_normalized, column_mappings)
    print("\n🎯 Resultado final:")
    print(df_final)
    
    # Verificar que no hay None
    none_count = df_final['nombre'].isna().sum()
    
    print(f"\n🔍 Verificación:")
    print(f"   None restantes: {none_count}")
    
    if none_count == 0:
        print("   ✅ TEST PASADO")
        return True
    else:
        print("   ❌ TEST FALLADO")
        return False


def test_varchar_with_custom_default():
    """Test: Columna VARCHAR con default personalizado ' ' (espacio)"""
    print_separator("TEST 5: Columna VARCHAR con default=' '")
    
    df = pd.DataFrame({
        'descripcion': ['Texto 1', None, '', 'Texto 2', np.nan]
    })
    
    print("📊 Datos originales:")
    print(df)
    
    # Normalizar
    df_normalized, _ = normalize_df_for_sql(df, strict=False)
    
    # Aplicar defaults con espacio
    column_mappings = {
        'descripcion': {
            'sql_type': 'NVARCHAR(255)',
            'nullable': False,
            'default_value': "' '"  # Espacio entre comillas
        }
    }
    
    df_final = apply_default_values_from_mappings(df_normalized, column_mappings)
    print("\n🎯 Resultado final:")
    print(df_final)
    print(f"\nValores exactos:")
    for idx, val in enumerate(df_final['descripcion']):
        print(f"   [{idx}] = '{val}' (len={len(str(val)) if pd.notna(val) else 0})")
    
    # Verificar que los None fueron reemplazados con espacio
    none_count = df_final['descripcion'].isna().sum()
    space_count = (df_final['descripcion'] == ' ').sum()
    
    print(f"\n🔍 Verificación:")
    print(f"   None restantes: {none_count}")
    print(f"   Espacios: {space_count}")
    
    if none_count == 0 and space_count > 0:
        print("   ✅ TEST PASADO")
        return True
    else:
        print("   ❌ TEST FALLADO")
        return False


def test_mixed_columns():
    """Test: Múltiples columnas con diferentes tipos y configuraciones"""
    print_separator("TEST 6: Múltiples columnas con diferentes configuraciones")
    
    df = pd.DataFrame({
        'id': [1, 2, 3, 4],
        'cantidad': [10, None, '', 20],
        'precio': [99.99, None, '', 150.50],
        'fecha': ['2024-01-15', None, '', '2024-01-17'],
        'nombre': ['Juan', None, '', 'Pedro'],
        'activo': [True, None, '', False]
    })
    
    print("📊 Datos originales:")
    print(df)
    
    # Normalizar
    df_normalized, _ = normalize_df_for_sql(df, strict=False)
    print("\n✅ Después de normalizar:")
    print(df_normalized)
    
    # Configuración mixta
    column_mappings = {
        'id': {'sql_type': 'INT', 'nullable': False, 'default_value': '0'},
        'cantidad': {'sql_type': 'INT', 'nullable': False, 'default_value': '0'},
        'precio': {'sql_type': 'FLOAT', 'nullable': False, 'default_value': '0.0'},
        'fecha': {'sql_type': 'DATE', 'nullable': False, 'default_value': 'GETDATE()'},
        'nombre': {'sql_type': 'NVARCHAR(100)', 'nullable': False, 'default_value': "' '"},
        'activo': {'sql_type': 'BIT', 'nullable': False, 'default_value': '0'}
    }
    
    df_final = apply_default_values_from_mappings(df_normalized, column_mappings)
    print("\n🎯 Resultado final:")
    print(df_final)
    print(f"\nTipos:")
    print(df_final.dtypes)
    
    # Verificar que no hay None en ninguna columna
    none_totals = df_final.isna().sum()
    print(f"\n🔍 None por columna:")
    print(none_totals)
    
    if none_totals.sum() == 0:
        print("   ✅ TEST PASADO (No hay None en ninguna columna)")
        return True
    else:
        print("   ❌ TEST FALLADO (Hay None restantes)")
        return False


def main():
    print("\n" + "🧪"*40)
    print("  PRUEBAS DE NORMALIZACIÓN DE VALORES VACÍOS")
    print("🧪"*40)
    
    results = []
    
    # Ejecutar todas las pruebas
    results.append(("INT nullable=False", test_int_column_not_nullable()))
    results.append(("INT nullable=True", test_int_column_nullable()))
    results.append(("DATE con GETDATE()", test_date_column_getdate()))
    results.append(("VARCHAR sin default", test_varchar_column()))
    results.append(("VARCHAR con espacio", test_varchar_with_custom_default()))
    results.append(("Múltiples columnas", test_mixed_columns()))
    
    # Resumen final
    print_separator("📊 RESUMEN DE PRUEBAS")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASADO" if result else "❌ FALLADO"
        print(f"   {name:<25} {status}")
    
    print(f"\n🎯 Total: {passed}/{total} pruebas pasadas")
    
    if passed == total:
        print("\n🎉 ¡TODOS LOS TESTS PASARON!")
        return 0
    else:
        print(f"\n⚠️ {total - passed} test(s) fallaron")
        return 1


if __name__ == "__main__":
    exit(main())
