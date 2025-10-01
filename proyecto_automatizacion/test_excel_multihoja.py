#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Prueba de la nueva implementación de procesamiento de Excel por hojas
Verifica que cada hoja del Excel se convierta en una tabla independiente
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

def crear_archivo_excel_prueba():
    """Crea un archivo Excel de prueba con múltiples hojas"""
    import pandas as pd
    import tempfile
    
    try:
        # Datos de prueba para diferentes hojas
        datos_hoja1 = {
            'ID': [1, 2, 3, 4],
            'Nombre': ['Juan', 'María', 'Pedro', 'Ana'],
            'Edad': [25, 30, 28, 35],
            'Ciudad': ['Madrid', 'Barcelona', 'Valencia', 'Sevilla']
        }
        
        datos_hoja2 = {
            'ProductoID': [101, 102, 103],
            'NombreProducto': ['Laptop', 'Mouse', 'Teclado'],
            'Precio': [599.99, 19.99, 49.99],
            'Stock': [50, 200, 100]
        }
        
        datos_hoja3 = {
            'VentaID': [1001, 1002, 1003, 1004, 1005],
            'Fecha': ['2025-01-01', '2025-01-02', '2025-01-03', '2025-01-04', '2025-01-05'],
            'Monto': [100.50, 250.00, 75.25, 300.00, 150.75],
            'ClienteID': [1, 2, 3, 1, 4]
        }
        
        # Crear DataFrames
        df_personas = pd.DataFrame(datos_hoja1)
        df_productos = pd.DataFrame(datos_hoja2)
        df_ventas = pd.DataFrame(datos_hoja3)
        
        # Crear archivo Excel temporal
        temp_dir = Path(tempfile.gettempdir())
        excel_path = temp_dir / 'prueba_excel_multihoja.xlsx'
        
        with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
            df_personas.to_excel(writer, sheet_name='Personas', index=False)
            df_productos.to_excel(writer, sheet_name='Productos', index=False)
            df_ventas.to_excel(writer, sheet_name='Ventas', index=False)
        
        print(f"📄 Archivo Excel de prueba creado: {excel_path}")
        print("📋 Hojas incluidas:")
        print(f"   - Personas: {len(df_personas)} registros")
        print(f"   - Productos: {len(df_productos)} registros")
        print(f"   - Ventas: {len(df_ventas)} registros")
        
        return str(excel_path)
        
    except Exception as e:
        print(f"❌ Error creando archivo Excel de prueba: {e}")
        return None

def crear_proceso_excel_prueba(excel_path):
    """Crea un proceso de migración para el Excel de prueba"""
    from automatizacion.models import DataSource, MigrationProcess
    import json
    
    try:
        # Crear fuente de datos
        source = DataSource.objects.create(
            name='Prueba_Excel_MultiHoja.xlsx',
            source_type='excel',
            file_path=excel_path
        )
        
        # Configurar hojas y columnas seleccionadas
        selected_sheets = ['Personas', 'Productos', 'Ventas']
        selected_columns = {
            'Personas': ['ID', 'Nombre', 'Edad', 'Ciudad'],
            'Productos': ['ProductoID', 'NombreProducto', 'Precio', 'Stock'],
            'Ventas': ['VentaID', 'Fecha', 'Monto', 'ClienteID']
        }
        
        # Crear proceso de migración
        process = MigrationProcess.objects.create(
            name='Prueba Excel Multi-Hoja',
            description='Proceso de prueba para verificar procesamiento por hojas separadas',
            source=source,
            selected_sheets=json.dumps(selected_sheets),
            selected_columns=json.dumps(selected_columns),
            target_db_name='DestinoAutomatizacion'
        )
        
        print(f"✅ Proceso de migración creado:")
        print(f"   ID: {process.id}")
        print(f"   Nombre: {process.name}")
        print(f"   Hojas seleccionadas: {selected_sheets}")
        print(f"   Fuente: {source.name}")
        
        return process
        
    except Exception as e:
        print(f"❌ Error creando proceso: {e}")
        return None

def verificar_estado_inicial():
    """Verifica el estado inicial de las tablas antes de la prueba"""
    from django.db import connections
    
    print("\n🔍 VERIFICANDO ESTADO INICIAL")
    print("=" * 50)
    
    try:
        # Verificar ProcesoLog
        with connections['logs'].cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM ProcesoLog")
            count_logs_antes = cursor.fetchone()[0]
        
        # Verificar ResultadosProcesados
        with connections['destino'].cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM ResultadosProcesados")
            count_resultados_antes = cursor.fetchone()[0]
        
        print(f"📊 Estado inicial:")
        print(f"   ProcesoLog: {count_logs_antes} registros")
        print(f"   ResultadosProcesados: {count_resultados_antes} registros")
        
        return count_logs_antes, count_resultados_antes
        
    except Exception as e:
        print(f"❌ Error verificando estado inicial: {e}")
        return 0, 0

def ejecutar_proceso_excel(process):
    """Ejecuta el proceso Excel y verifica los resultados"""
    print(f"\n🚀 EJECUTANDO PROCESO EXCEL: '{process.name}'")
    print("=" * 60)
    
    try:
        # Ejecutar el proceso
        process.run()
        
        print("✅ Proceso ejecutado sin errores")
        return True
        
    except Exception as e:
        print(f"❌ Error ejecutando proceso: {e}")
        import traceback
        traceback.print_exc()
        return False

def verificar_resultados(count_logs_antes, count_resultados_antes):
    """Verifica que se hayan creado los registros esperados"""
    from django.db import connections
    
    print(f"\n🔍 VERIFICANDO RESULTADOS DESPUÉS DE LA EJECUCIÓN")
    print("=" * 60)
    
    try:
        # Verificar ProcesoLog
        with connections['logs'].cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM ProcesoLog")
            count_logs_despues = cursor.fetchone()[0]
            
            # Obtener últimos logs
            cursor.execute("""
                SELECT TOP 5 
                    LogID, ProcesoID, NombreProceso, Estado, FechaHora
                FROM ProcesoLog 
                ORDER BY FechaHora DESC
            """)
            ultimos_logs = cursor.fetchall()
        
        # Verificar ResultadosProcesados
        with connections['destino'].cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM ResultadosProcesados")
            count_resultados_despues = cursor.fetchone()[0]
            
            # Obtener últimos resultados
            cursor.execute("""
                SELECT TOP 5
                    ResultadoID, ProcesoID, NombreProceso, EstadoProceso, 
                    RegistrosAfectados, FechaRegistro
                FROM ResultadosProcesados 
                ORDER BY FechaRegistro DESC
            """)
            ultimos_resultados = cursor.fetchall()
        
        # Verificar tablas dinámicas creadas
        with connections['destino'].cursor() as cursor:
            cursor.execute("""
                SELECT TABLE_NAME 
                FROM INFORMATION_SCHEMA.TABLES 
                WHERE TABLE_NAME LIKE 'Proceso_%'
                ORDER BY TABLE_NAME
            """)
            tablas_creadas = cursor.fetchall()
        
        # Mostrar estadísticas
        logs_nuevos = count_logs_despues - count_logs_antes
        resultados_nuevos = count_resultados_despues - count_resultados_antes
        
        print(f"📊 ESTADÍSTICAS:")
        print(f"   ProcesoLog: {count_logs_antes} → {count_logs_despues} (+{logs_nuevos})")
        print(f"   ResultadosProcesados: {count_resultados_antes} → {count_resultados_despues} (+{resultados_nuevos})")
        print(f"   Tablas dinámicas encontradas: {len(tablas_creadas)}")
        
        # Mostrar últimos logs
        print(f"\n📋 ÚLTIMOS LOGS CREADOS:")
        for log in ultimos_logs:
            print(f"   LogID: {log[0]} | Proceso: {log[2]} | Estado: {log[3]} | Fecha: {log[4]}")
        
        # Mostrar últimos resultados
        print(f"\n📋 ÚLTIMOS RESULTADOS CREADOS:")
        for resultado in ultimos_resultados:
            print(f"   ID: {resultado[0]} | Proceso: {resultado[2]} | Estado: {resultado[3]} | Registros: {resultado[4]} | Fecha: {resultado[5]}")
        
        # Mostrar tablas creadas
        print(f"\n📋 TABLAS DINÁMICAS EXISTENTES:")
        for tabla in tablas_creadas:
            tabla_name = tabla[0]
            
            # Contar registros en cada tabla
            try:
                with connections['destino'].cursor() as cursor:
                    cursor.execute(f"SELECT COUNT(*) FROM [{tabla_name}]")
                    count_tabla = cursor.fetchone()[0]
                print(f"   {tabla_name}: {count_tabla} registros")
            except:
                print(f"   {tabla_name}: Error contando registros")
        
        # Verificaciones específicas para Excel
        esperados_logs = 4  # 1 proceso principal + 3 hojas
        esperados_resultados = 3  # 3 hojas (cada hoja genera su resultado)
        esperadas_tablas_nuevas = ['Proceso_Personas', 'Proceso_Productos', 'Proceso_Ventas']
        
        print(f"\n✅ VERIFICACIONES:")
        print(f"   Logs esperados: {esperados_logs}, Obtenidos: {logs_nuevos} - {'✅' if logs_nuevos >= esperados_logs else '❌'}")
        print(f"   Resultados esperados: {esperados_resultados}, Obtenidos: {resultados_nuevos} - {'✅' if resultados_nuevos >= esperados_resultados else '❌'}")
        
        # Verificar que se crearon las tablas esperadas
        tablas_existentes = [t[0] for t in tablas_creadas]
        tablas_encontradas = 0
        for tabla_esperada in esperadas_tablas_nuevas:
            if tabla_esperada in tablas_existentes:
                tablas_encontradas += 1
                print(f"   Tabla {tabla_esperada}: ✅ Encontrada")
            else:
                print(f"   Tabla {tabla_esperada}: ❌ No encontrada")
        
        exito_general = (
            logs_nuevos >= esperados_logs and 
            resultados_nuevos >= esperados_resultados and 
            tablas_encontradas >= len(esperadas_tablas_nuevas)
        )
        
        return exito_general
        
    except Exception as e:
        print(f"❌ Error verificando resultados: {e}")
        import traceback
        traceback.print_exc()
        return False

def limpiar_datos_prueba(process):
    """Limpia los datos de prueba creados"""
    print(f"\n🧹 LIMPIANDO DATOS DE PRUEBA")
    print("=" * 40)
    
    try:
        # Eliminar proceso y fuente de datos
        source = process.source
        process.delete()
        source.delete()
        
        # Eliminar archivo temporal
        import os
        if os.path.exists(source.file_path):
            os.remove(source.file_path)
            print(f"✅ Archivo temporal eliminado: {source.file_path}")
        
        print("✅ Datos de prueba eliminados correctamente")
        
    except Exception as e:
        print(f"⚠️ Error limpiando datos de prueba: {e}")

if __name__ == '__main__':
    print("🧪 PRUEBA: PROCESAMIENTO DE EXCEL POR HOJAS INDIVIDUALES")
    print("=" * 70)
    
    # 1. Crear archivo Excel de prueba
    excel_path = crear_archivo_excel_prueba()
    if not excel_path:
        print("❌ No se pudo crear el archivo Excel de prueba")
        exit(1)
    
    # 2. Crear proceso
    process = crear_proceso_excel_prueba(excel_path)
    if not process:
        print("❌ No se pudo crear el proceso de prueba")
        exit(1)
    
    try:
        # 3. Verificar estado inicial
        count_logs_antes, count_resultados_antes = verificar_estado_inicial()
        
        # 4. Ejecutar proceso
        exito_ejecucion = ejecutar_proceso_excel(process)
        
        if exito_ejecucion:
            # 5. Verificar resultados
            exito_verificacion = verificar_resultados(count_logs_antes, count_resultados_antes)
            
            # 6. Resultado final
            print(f"\n{'='*70}")
            if exito_verificacion:
                print("🎉 ¡PRUEBA EXITOSA!")
                print("✅ El procesamiento de Excel por hojas individuales funciona correctamente")
                print("✅ Cada hoja se convirtió en una tabla independiente")
                print("✅ Se crearon registros en ProcesoLog y ResultadosProcesados")
                print("✅ La implementación está lista para usar en producción")
            else:
                print("⚠️ PRUEBA PARCIALMENTE EXITOSA")
                print("✅ El proceso se ejecutó sin errores")
                print("❌ Algunos resultados esperados no se encontraron")
                print("🔍 Revisa los detalles de verificación arriba")
        else:
            print(f"\n{'='*70}")
            print("❌ PRUEBA FALLIDA")
            print("❌ El proceso no se ejecutó correctamente")
            print("🔍 Revisa los errores mostrados arriba")
    
    finally:
        # 7. Limpiar datos de prueba
        limpiar_datos_prueba(process)