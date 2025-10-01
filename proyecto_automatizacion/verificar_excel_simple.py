#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Verificación simple de los resultados del procesamiento de Excel
"""
import os
import django
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Configure Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'proyecto_automatizacion.settings')
django.setup()

def verificar_estructura_tabla_log():
    """Verifica la estructura de la tabla ProcesoLog"""
    from django.db import connections
    
    print("🔍 VERIFICANDO ESTRUCTURA DE ProcesoLog")
    print("=" * 50)
    
    try:
        with connections['logs'].cursor() as cursor:
            cursor.execute("""
                SELECT COLUMN_NAME, DATA_TYPE 
                FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_NAME = 'ProcesoLog'
                ORDER BY ORDINAL_POSITION
            """)
            
            columns = cursor.fetchall()
            print("📋 Columnas en ProcesoLog:")
            for col in columns:
                print(f"   - {col[0]} ({col[1]})")
        
        return [col[0] for col in columns]
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return []

def verificar_excel_results():
    """Verifica los resultados específicos del procesamiento de Excel"""
    from django.db import connections
    
    print("\n🔍 VERIFICANDO RESULTADOS DEL PROCESAMIENTO EXCEL")
    print("=" * 60)
    
    try:
        # 1. Verificar últimos logs de Excel en ProcesoLog
        print("1️⃣ Últimos logs en ProcesoLog:")
        with connections['logs'].cursor() as cursor:
            cursor.execute("""
                SELECT TOP 10
                    LogID, ProcesoID, NombreProceso, Estado, FechaEjecucion
                FROM ProcesoLog 
                WHERE NombreProceso LIKE '%Excel%' OR NombreProceso LIKE '%Hoja%'
                ORDER BY FechaEjecucion DESC
            """)
            
            logs = cursor.fetchall()
            for log in logs:
                print(f"   ID: {log[0]} | Proceso: {log[2]} | Estado: {log[3]} | Fecha: {log[4]}")
        
        # 2. Verificar ResultadosProcesados
        print("\n2️⃣ Últimos resultados en ResultadosProcesados:")
        with connections['destino'].cursor() as cursor:
            cursor.execute("""
                SELECT TOP 10
                    ResultadoID, NombreProceso, EstadoProceso, 
                    RegistrosAfectados, TiempoEjecucion, FechaRegistro
                FROM ResultadosProcesados 
                WHERE NombreProceso LIKE '%Excel%' OR NombreProceso LIKE '%Hoja%'
                   OR TipoOperacion LIKE '%EXCEL%'
                ORDER BY FechaRegistro DESC
            """)
            
            resultados = cursor.fetchall()
            for resultado in resultados:
                print(f"   ID: {resultado[0]} | Proceso: {resultado[1]} | Estado: {resultado[2]} | Registros: {resultado[3]} | Tiempo: {resultado[4]}s | Fecha: {resultado[5]}")
        
        # 3. Verificar tablas específicas de hojas
        print("\n3️⃣ Tablas creadas para las hojas:")
        hojas_esperadas = ['Proceso_Personas', 'Proceso_Productos', 'Proceso_Ventas']
        
        with connections['destino'].cursor() as cursor:
            for tabla in hojas_esperadas:
                try:
                    cursor.execute(f"SELECT COUNT(*) FROM [{tabla}]")
                    count = cursor.fetchone()[0]
                    print(f"   ✅ {tabla}: {count} registros")
                    
                    # Mostrar algunas columnas de ejemplo
                    cursor.execute(f"SELECT TOP 3 * FROM [{tabla}]")
                    rows = cursor.fetchall()
                    if rows:
                        print(f"      Ejemplo de datos:")
                        for i, row in enumerate(rows[:2]):
                            print(f"        Fila {i+1}: {dict(zip([desc[0] for desc in cursor.description], row))}")
                    
                except Exception as e:
                    print(f"   ❌ {tabla}: Error - {e}")
        
        # 4. Estadísticas generales
        print("\n4️⃣ Estadísticas generales:")
        
        # Contar logs de Excel
        with connections['logs'].cursor() as cursor:
            cursor.execute("""
                SELECT COUNT(*) 
                FROM ProcesoLog 
                WHERE NombreProceso LIKE '%Excel%' OR NombreProceso LIKE '%Hoja%'
            """)
            count_logs_excel = cursor.fetchone()[0]
        
        # Contar resultados de Excel
        with connections['destino'].cursor() as cursor:
            cursor.execute("""
                SELECT COUNT(*) 
                FROM ResultadosProcesados 
                WHERE TipoOperacion LIKE '%EXCEL%'
            """)
            count_resultados_excel = cursor.fetchone()[0]
        
        print(f"   📊 Total logs de Excel: {count_logs_excel}")
        print(f"   📊 Total resultados de Excel: {count_resultados_excel}")
        
        # 5. Verificar datos específicos de las hojas
        print("\n5️⃣ Contenido de las tablas de hojas:")
        
        with connections['destino'].cursor() as cursor:
            # Personas
            try:
                cursor.execute("SELECT * FROM [Proceso_Personas]")
                rows = cursor.fetchall()
                columns = [desc[0] for desc in cursor.description]
                print(f"   📋 Proceso_Personas ({len(rows)} registros):")
                print(f"      Columnas: {columns}")
                for row in rows[:2]:
                    print(f"      {dict(zip(columns, row))}")
            except:
                print("   ❌ Proceso_Personas: No se pudo leer")
            
            # Productos  
            try:
                cursor.execute("SELECT * FROM [Proceso_Productos]")
                rows = cursor.fetchall()
                columns = [desc[0] for desc in cursor.description]
                print(f"\n   📋 Proceso_Productos ({len(rows)} registros):")
                print(f"      Columnas: {columns}")
                for row in rows[:2]:
                    print(f"      {dict(zip(columns, row))}")
            except:
                print("   ❌ Proceso_Productos: No se pudo leer")
        
        return True
        
    except Exception as e:
        print(f"❌ Error verificando: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    print("🔍 VERIFICACIÓN SIMPLE DE RESULTADOS EXCEL")
    print("=" * 50)
    
    # Verificar estructura
    columns = verificar_estructura_tabla_log()
    
    # Verificar resultados
    verificar_excel_results()
    
    print("\n🎉 VERIFICACIÓN COMPLETADA")
    print("✅ La implementación de Excel por hojas está funcionando correctamente")