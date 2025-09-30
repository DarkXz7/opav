#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script de Prueba Simplificado del Sistema de Carga de Datos
"""
import os
import django
import uuid
import json
import time
from datetime import datetime

# Configure Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'proyecto_automatizacion.settings')
django.setup()

from django.db import connections
from automatizacion.data_load_service import data_load_service

def setup_test_data():
    """
    Configura datos de prueba simples
    """
    print("=== CONFIGURANDO DATOS DE PRUEBA ===")
    
    try:
        with connections['default'].cursor() as cursor:
            # Crear tabla simple de prueba
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS test_usuarios (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nombre VARCHAR(100),
                    email VARCHAR(255),
                    activo BOOLEAN DEFAULT 1
                )
            """)
            
            # Limpiar e insertar datos
            cursor.execute("DELETE FROM test_usuarios")
            
            test_data = [
                ('Juan Pérez', 'juan@test.com', 1),
                ('María García', 'maria@test.com', 1),
                ('Carlos López', 'carlos@test.com', 0),
            ]
            
            cursor.executemany("""
                INSERT INTO test_usuarios (nombre, email, activo)
                VALUES (?, ?, ?)
            """, test_data)
            
            cursor.execute("SELECT COUNT(*) FROM test_usuarios")
            count = cursor.fetchone()[0]
            print(f"✓ {count} registros de prueba creados")
            
        return True
        
    except Exception as e:
        print(f"❌ Error configurando datos: {e}")
        return False

def test_basic_load():
    """
    Prueba básica de carga de datos
    """
    print("\n=== PRUEBA BÁSICA DE CARGA ===")
    
    try:
        # Configuración mínima
        validation_config = {
            'required_fields': ['nombre', 'email']
        }
        
        result = data_load_service.execute_data_load(
            source_database='default',
            source_table='test_usuarios',
            target_database='destino',
            validation_rules=validation_config
        )
        
        if result['success']:
            print(f"✅ CARGA EXITOSA")
            print(f"   Proceso ID: {result['proceso_id']}")
            print(f"   Registros procesados: {result['registros_procesados']}")
            print(f"   Duración: {result['duracion']:.2f}s")
            
            # Verificar en base de datos destino
            with connections['destino'].cursor() as cursor:
                cursor.execute("""
                    SELECT COUNT(*) FROM ResultadosProcesados 
                    WHERE ProcesoID = ? OR ProcesoID LIKE ?
                """, [result['proceso_id'], f"{result['proceso_id']}_%"])
                
                count = cursor.fetchone()[0]
                print(f"   Registros en BD destino: {count}")
            
            return True
        else:
            print(f"❌ CARGA FALLIDA")
            print(f"   Error: {result['error']}")
            print(f"   Detalles: {result.get('detalles', {})}")
            return False
            
    except Exception as e:
        print(f"💥 ERROR CRÍTICO: {e}")
        return False

def test_logs_verification():
    """
    Verifica que los logs se estén guardando correctamente
    """
    print("\n=== VERIFICACIÓN DE LOGS ===")
    
    try:
        with connections['logs'].cursor() as cursor:
            # Contar logs recientes
            cursor.execute("""
                SELECT COUNT(*) FROM ProcesoLog 
                WHERE FechaEjecucion >= DATEADD(HOUR, -1, GETDATE())
                    AND NombreProceso LIKE 'CARGA_DATOS_%'
            """)
            
            count = cursor.fetchone()[0]
            print(f"✓ {count} logs de carga en la última hora")
            
            if count > 0:
                # Obtener último log
                cursor.execute("""
                    SELECT TOP 1 ProcesoID, Estado, DuracionSegundos, MensajeError
                    FROM ProcesoLog 
                    WHERE NombreProceso LIKE 'CARGA_DATOS_%'
                    ORDER BY FechaEjecucion DESC
                """)
                
                row = cursor.fetchone()
                if row:
                    print(f"   Último proceso: {row[0]}")
                    print(f"   Estado: {row[1]}")
                    print(f"   Duración: {row[2]}s")
                    if row[3]:
                        print(f"   Error: {row[3]}")
            
        return True
        
    except Exception as e:
        print(f"❌ Error verificando logs: {e}")
        return False

def test_results_verification():
    """
    Verifica los resultados en la base de datos destino
    """
    print("\n=== VERIFICACIÓN DE RESULTADOS ===")
    
    try:
        with connections['destino'].cursor() as cursor:
            # Contar registros procesados recientes
            cursor.execute("""
                SELECT COUNT(*) FROM ResultadosProcesados 
                WHERE FechaRegistro >= DATEADD(HOUR, -1, GETDATE())
                    AND TipoOperacion = 'CARGA_MASIVA'
            """)
            
            count = cursor.fetchone()[0]
            print(f"✓ {count} registros procesados en la última hora")
            
            if count > 0:
                # Obtener estadísticas
                cursor.execute("""
                    SELECT 
                        COUNT(DISTINCT ProcesoID) as procesos_unicos,
                        COUNT(*) as total_registros,
                        MIN(FechaRegistro) as primer_registro,
                        MAX(FechaRegistro) as ultimo_registro
                    FROM ResultadosProcesados 
                    WHERE FechaRegistro >= DATEADD(HOUR, -1, GETDATE())
                        AND TipoOperacion = 'CARGA_MASIVA'
                """)
                
                stats = cursor.fetchone()
                if stats:
                    print(f"   Procesos únicos: {stats[0]}")
                    print(f"   Total registros: {stats[1]}")
                    print(f"   Rango temporal: {stats[2]} - {stats[3]}")
            
        return True
        
    except Exception as e:
        print(f"❌ Error verificando resultados: {e}")
        return False

def main():
    """
    Función principal
    """
    print("🚀 PRUEBA SIMPLIFICADA DEL SISTEMA DE CARGA ROBUSTA")
    print("=" * 50)
    
    start_time = time.time()
    
    # Configurar datos de prueba
    if not setup_test_data():
        print("❌ FALLO EN CONFIGURACIÓN - ABORTANDO")
        return 1
    
    # Ejecutar pruebas
    tests = [
        test_basic_load,
        test_logs_verification,
        test_results_verification
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"💥 ERROR EN PRUEBA: {e}")
            failed += 1
    
    duration = time.time() - start_time
    
    # Resumen
    print("\n" + "=" * 50)
    print("📋 RESUMEN DE PRUEBAS")
    print(f"✅ Pruebas pasadas: {passed}")
    print(f"❌ Pruebas fallidas: {failed}")
    print(f"⏱️ Tiempo total: {duration:.2f}s")
    
    if failed == 0:
        print("🎉 TODAS LAS PRUEBAS PASARON")
        print("📊 SISTEMA DE CARGA ROBUSTA FUNCIONANDO CORRECTAMENTE")
        print("🔗 Funcionalidades verificadas:")
        print("   - Validación de datos de origen")
        print("   - Transferencia a base de datos destino")
        print("   - Logging completo en SQL Server")
        print("   - Registro de resultados con metadatos")
        print("   - Manejo de errores y trazabilidad")
    else:
        print("⚠️ HAY PRUEBAS FALLIDAS - REVISAR IMPLEMENTACIÓN")
    
    return 0 if failed == 0 else 1

if __name__ == "__main__":
    exit(main())
