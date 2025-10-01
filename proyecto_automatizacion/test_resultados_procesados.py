#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script de prueba para verificar el guardado en ResultadosProcesados
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

def test_resultados_procesados_save():
    """Prueba el guardado en ResultadosProcesados"""
    try:
        from automatizacion.models_destino import ResultadosProcesados
        from automatizacion.models import MigrationProcess
        from django.db import connections
        import json
        from datetime import datetime
        
        print("🧪 PRUEBA: Guardado en ResultadosProcesados")
        print("=" * 60)
        
        # 1. Verificar conexión a DestinoAutomatizacion
        print("1️⃣ Verificando conexión a DestinoAutomatizacion...")
        try:
            with connections['destino'].cursor() as cursor:
                cursor.execute("SELECT COUNT(*) FROM ResultadosProcesados")
                count_before = cursor.fetchone()[0]
            print(f"   ✅ Conexión OK - Registros actuales: {count_before}")
        except Exception as e:
            print(f"   ❌ Error conexión: {e}")
            return False
        
        # 2. Buscar un proceso existente para probar
        print("\n2️⃣ Buscando procesos existentes...")
        processes = list(MigrationProcess.objects.all()[:3])
        if not processes:
            print("   ⚠️ No hay procesos configurados para probar")
            return False
        
        print(f"   ✅ Encontrados {len(processes)} procesos:")
        for proc in processes:
            print(f"      - ID: {proc.id}, Nombre: '{proc.name}'")
        
        # 3. Probar guardado manual en ResultadosProcesados
        print("\n3️⃣ Probando guardado manual...")
        test_proceso = processes[0]
        
        test_data = {
            'tabla_destino': f'Proceso_{test_proceso.name.replace(" ", "_")}',
            'campos_columnas': ['campo1', 'campo2', 'campo3'],
            'total_registros_cargados': 150,
            'estado_final': 'COMPLETADO',
            'timestamp_procesamiento': datetime.now().isoformat()
        }
        
        metadatos = {
            'version_proceso': '1.0',
            'parametros_usados': {'test': True},
            'duracion_segundos': 12.5,
            'tabla_creada': f'Proceso_{test_proceso.name.replace(" ", "_")}'
        }
        
        resultado_test = ResultadosProcesados(
            ProcesoID=f"TEST-{test_proceso.id}-{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            NombreProceso=f"PRUEBA: {test_proceso.name}",
            DatosProcesados=json.dumps(test_data, ensure_ascii=False),
            UsuarioResponsable='script_prueba',
            EstadoProceso='COMPLETADO',
            TipoOperacion=f'PRUEBA_MIGRACION_{test_proceso.name.upper().replace(" ", "_")}',
            RegistrosAfectados=150,
            TiempoEjecucion=12.5,
            MetadatosProceso=json.dumps(metadatos, ensure_ascii=False)
        )
        
        resultado_test.save(using='destino')
        print(f"   ✅ Registro guardado con ID: {resultado_test.ResultadoID}")
        
        # 4. Verificar que se guardó correctamente
        print("\n4️⃣ Verificando registro guardado...")
        try:
            with connections['destino'].cursor() as cursor:
                cursor.execute("""
                    SELECT TOP 1 
                        ResultadoID, ProcesoID, NombreProceso, EstadoProceso, 
                        RegistrosAfectados, TiempoEjecucion, FechaRegistro
                    FROM ResultadosProcesados 
                    WHERE ProcesoID LIKE 'TEST-%'
                    ORDER BY FechaRegistro DESC
                """)
                
                row = cursor.fetchone()
                if row:
                    print("   ✅ Registro encontrado:")
                    print(f"      ResultadoID: {row[0]}")
                    print(f"      ProcesoID: {row[1]}")
                    print(f"      NombreProceso: {row[2]}")
                    print(f"      EstadoProceso: {row[3]}")
                    print(f"      RegistrosAfectados: {row[4]}")
                    print(f"      TiempoEjecucion: {row[5]}")
                    print(f"      FechaRegistro: {row[6]}")
                else:
                    print("   ❌ No se encontró el registro")
                    return False
                    
        except Exception as e:
            print(f"   ❌ Error verificando registro: {e}")
            return False
        
        # 5. Verificar estructura completa de la tabla
        print("\n5️⃣ Verificando estructura de ResultadosProcesados...")
        try:
            with connections['destino'].cursor() as cursor:
                cursor.execute("""
                    SELECT COLUMN_NAME, DATA_TYPE, IS_NULLABLE 
                    FROM INFORMATION_SCHEMA.COLUMNS 
                    WHERE TABLE_NAME = 'ResultadosProcesados'
                    ORDER BY ORDINAL_POSITION
                """)
                
                columns = cursor.fetchall()
                print("   ✅ Columnas encontradas:")
                for col in columns:
                    print(f"      - {col[0]} ({col[1]}) - Null: {col[2]}")
        except Exception as e:
            print(f"   ⚠️ Error verificando estructura: {e}")
        
        # 6. Contar registros totales
        print("\n6️⃣ Conteo final de registros...")
        try:
            with connections['destino'].cursor() as cursor:
                cursor.execute("SELECT COUNT(*) FROM ResultadosProcesados")
                count_after = cursor.fetchone()[0]
            print(f"   📊 Registros antes: {count_before}")
            print(f"   📊 Registros después: {count_after}")
            print(f"   📊 Nuevos registros: {count_after - count_before}")
        except Exception as e:
            print(f"   ❌ Error contando: {e}")
        
        print("\n🎉 PRUEBA COMPLETADA EXITOSAMENTE")
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR EN PRUEBA: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_proceso_completo():
    """Prueba la ejecución completa de un proceso con guardado automático"""
    try:
        from automatizacion.models import MigrationProcess
        
        print("\n" + "="*60)
        print("🚀 PRUEBA: Ejecución completa de proceso")
        print("=" * 60)
        
        # Buscar un proceso para ejecutar
        processes = list(MigrationProcess.objects.all()[:1])
        if not processes:
            print("⚠️ No hay procesos para ejecutar")
            return False
        
        test_process = processes[0]
        print(f"📋 Proceso a ejecutar: '{test_process.name}' (ID: {test_process.id})")
        
        # Verificar registros antes
        from django.db import connections
        with connections['destino'].cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM ResultadosProcesados")
            count_before = cursor.fetchone()[0]
        
        print(f"📊 Registros en ResultadosProcesados antes: {count_before}")
        
        # Ejecutar proceso
        print("🏃 Ejecutando proceso...")
        test_process.run()
        
        # Verificar registros después
        with connections['destino'].cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM ResultadosProcesados")
            count_after = cursor.fetchone()[0]
        
        print(f"📊 Registros en ResultadosProcesados después: {count_after}")
        print(f"📊 Nuevos registros creados: {count_after - count_before}")
        
        # Mostrar últimos registros
        with connections['destino'].cursor() as cursor:
            cursor.execute("""
                SELECT TOP 3
                    ResultadoID, ProcesoID, NombreProceso, EstadoProceso, 
                    RegistrosAfectados, FechaRegistro
                FROM ResultadosProcesados 
                ORDER BY FechaRegistro DESC
            """)
            
            rows = cursor.fetchall()
            print("\n📋 Últimos registros en ResultadosProcesados:")
            for row in rows:
                print(f"   ID: {row[0]} | Proceso: {row[1][:20]}... | Nombre: {row[2]} | Estado: {row[3]} | Registros: {row[4]} | Fecha: {row[5]}")
        
        print("🎉 PRUEBA DE PROCESO COMPLETO EXITOSA")
        return True
        
    except Exception as e:
        print(f"❌ ERROR EN PRUEBA DE PROCESO: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    print("🧪 INICIANDO PRUEBAS DE RESULTADOS PROCESADOS")
    print("=" * 60)
    
    # Ejecutar pruebas
    test1_ok = test_resultados_procesados_save()
    
    if test1_ok:
        test2_ok = test_proceso_completo()
    else:
        print("❌ Saltando prueba de proceso por error anterior")
        test2_ok = False
    
    print("\n" + "="*60)
    print("📊 RESUMEN DE PRUEBAS:")
    print(f"   Guardado manual: {'✅ PASSED' if test1_ok else '❌ FAILED'}")
    print(f"   Proceso completo: {'✅ PASSED' if test2_ok else '❌ FAILED'}")
    
    if test1_ok and test2_ok:
        print("🎉 TODAS LAS PRUEBAS PASARON")
    else:
        print("⚠️ ALGUNAS PRUEBAS FALLARON")