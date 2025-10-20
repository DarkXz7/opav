"""
Script de prueba para validar la normalización de datos SQL
Ejecutar desde la raíz del proyecto Django
"""
import os
import sys
import django
import pandas as pd
import numpy as np
from datetime import datetime

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'proyecto_automatizacion.settings')
django.setup()

from automatizacion.sql_utils import normalize_df_for_sql

def test_normalization():
    """Prueba la función de normalización con casos comunes problemáticos"""
    
    print("=" * 80)
    print("🧪 PRUEBA DE NORMALIZACIÓN DE DATOS SQL")
    print("=" * 80)
    
    # Crear DataFrame de prueba con datos problemáticos
    test_data = {
        'ID': [1, 2, 3, 4, 5, None, 7],
        'Nombre': ['Juan', 'María', '', '  ', None, 'Pedro', 'Ana'],
        'Edad': [25, '30', 'abc', '', None, 45.5, 50],
        'Salario': ['1000.50', '2000.00', 'N/A', '', np.nan, '3500.75', '4000.00'],
        'Fecha_Ingreso': ['2020-01-15', '2021-06-20', 'fecha_invalida', '', None, '2023-03-10', datetime(2024, 5, 1)],
        'Activo': [True, False, 'Si', 'No', 1, 0, None]
    }
    
    df_original = pd.DataFrame(test_data)
    
    print("\n📋 DATAFRAME ORIGINAL:")
    print(df_original)
    print(f"\nTipos de datos originales:")
    print(df_original.dtypes)
    
    print("\n" + "=" * 80)
    print("🔄 APLICANDO NORMALIZACIÓN...")
    print("=" * 80)
    
    # Normalizar (modo no estricto - convierte errores a None)
    df_normalized, issues = normalize_df_for_sql(df_original, strict=False)
    
    print("\n✅ DATAFRAME NORMALIZADO:")
    print(df_normalized)
    print(f"\nTipos de datos normalizados:")
    print(df_normalized.dtypes)
    
    if issues:
        print("\n⚠️ PROBLEMAS DETECTADOS DURANTE LA NORMALIZACIÓN:")
        for issue in issues:
            print(f"   - Columna '{issue['column']}': {issue['count']} valores inválidos")
            print(f"     Ejemplo: {issue.get('example', 'N/A')}")
    else:
        print("\n✅ No se detectaron problemas de normalización")
    
    print("\n" + "=" * 80)
    print("🔍 ANÁLISIS DETALLADO POR COLUMNA:")
    print("=" * 80)
    
    for col in df_normalized.columns:
        print(f"\n📊 Columna: {col}")
        print(f"   Original: {df_original[col].dtype}")
        print(f"   Normalizado: {df_normalized[col].dtype}")
        print(f"   Valores None (NULL): {df_normalized[col].isna().sum()}")
        print(f"   Valores únicos: {df_normalized[col].nunique()}")
        
        # Mostrar cambios
        cambios = []
        for idx in range(len(df_original)):
            val_orig = df_original[col].iloc[idx]
            val_norm = df_normalized[col].iloc[idx]
            if str(val_orig) != str(val_norm) and not (pd.isna(val_orig) and pd.isna(val_norm)):
                cambios.append(f"      Fila {idx}: '{val_orig}' → '{val_norm}'")
        
        if cambios:
            print(f"   Cambios detectados:")
            for cambio in cambios[:3]:  # Mostrar máximo 3 ejemplos
                print(cambio)
            if len(cambios) > 3:
                print(f"      ... y {len(cambios) - 3} cambios más")
    
    print("\n" + "=" * 80)
    print("🎯 PRUEBA DE MODO ESTRICTO (strict=True)")
    print("=" * 80)
    
    try:
        df_strict, issues_strict = normalize_df_for_sql(df_original, strict=True)
        print("✅ Normalización estricta completada sin errores")
    except ValueError as e:
        print(f"❌ Error esperado en modo estricto:")
        print(f"   {str(e)}")
    
    print("\n" + "=" * 80)
    print("✅ PRUEBA COMPLETADA")
    print("=" * 80)
    print("\n💡 Interpretación de resultados:")
    print("   - Valores convertidos a None serán NULL en SQL Server")
    print("   - Cadenas vacías y espacios en blanco → None")
    print("   - Valores no numéricos en columnas numéricas → None")
    print("   - Fechas inválidas → None")
    print("   - El modo no estricto (strict=False) es más tolerante")
    print("   - El modo estricto (strict=True) lanza error si hay problemas")
    
    return df_normalized, issues

if __name__ == '__main__':
    try:
        df_result, issues_result = test_normalization()
        
        # Resumen final
        print("\n" + "=" * 80)
        print("📊 RESUMEN:")
        print(f"   Filas procesadas: {len(df_result)}")
        print(f"   Columnas: {len(df_result.columns)}")
        print(f"   Problemas detectados: {len(issues_result)}")
        print(f"   Total de NULL generados: {df_result.isna().sum().sum()}")
        print("=" * 80)
        
    except Exception as e:
        print(f"\n❌ ERROR EN LA PRUEBA:")
        print(f"   {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
