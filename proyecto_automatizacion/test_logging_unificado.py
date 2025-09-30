#!/usr/bin/env python
"""
Script de prueba para verificar el sistema de logging unificado
- Solo un registro por proceso en LogsAutomatizacion
- Datos insertados correctamente en DestinoAutomatizacion
- Mensajes presentables en lugar de NULL
"""

import os
import sys
import django
from datetime import datetime
import uuid

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'proyecto_automatizacion.settings')
django.setup()

from django.contrib.auth.models import User
from automatizacion.models import MigrationProcess, DataSource, DatabaseConnection
from automatizacion.logs.models_logs import ProcesoLog
from automatizacion.models_destino import ResultadosProcesados
from automatizacion.web_logger_optimized import registrar_proceso_web, finalizar_proceso_web

def test_logging_unificado():
    """Test del sistema de logging unificado"""
    
    print("=" * 80)
    print("🧪 PRUEBA: Sistema de Logging Unificado")
    print("=" * 80)
    
    # Limpiar registros previos de prueba
    ProcesoLog.objects.filter(NombreProceso__icontains="TEST_LOGGING_UNIFICADO").using('logs').delete()
    ResultadosProcesados.objects.filter(Tipo__icontains="TEST_LOGGING_UNIFICADO").using('destino').delete()
    
    try:
        # Crear o usar usuario de prueba
        user, created = User.objects.get_or_create(
            username='test_logging',
            defaults={'email': 'test@logging.com', 'first_name': 'Test', 'last_name': 'Logging'}
        )
        
        # 1. Probar registrar_proceso_web + finalizar_proceso_web
        print("\n1️⃣ Probando registrar_proceso_web...")
        tracker, proceso_id = registrar_proceso_web(
            nombre_proceso="TEST_LOGGING_UNIFICADO_PROCESO_1",
            usuario=user,
            datos_adicionales={'test': 'logging_unificado', 'timestamp': datetime.now().isoformat()}
        )
        
        if tracker and proceso_id:
            print(f"   ✅ Proceso iniciado. ID: {proceso_id}")
            
            # Actualizar estado intermedio
            tracker.actualizar_estado("EN_PROGRESO", "Procesando datos de prueba...")
            print(f"   ✅ Estado actualizado a EN_PROGRESO")
            
            # Finalizar con éxito
            finalizar_proceso_web(
                tracker,
                usuario=user,
                exito=True,
                detalles="Test de logging unificado completado exitosamente"
            )
            print(f"   ✅ Proceso finalizado con éxito")
            
        else:
            print(f"   ❌ Error al iniciar proceso")
            return False
            
        # 2. Verificar que solo hay UN registro en LogsAutomatizacion
        print("\n2️⃣ Verificando registros únicos en LogsAutomatizacion...")
        logs = ProcesoLog.objects.filter(ProcesoID=proceso_id).using('logs')
        count_logs = logs.count()
        
        if count_logs == 1:
            print(f"   ✅ Solo 1 registro encontrado (correcto): {count_logs}")
            log_record = logs.first()
            print(f"   📋 Estado: {log_record.Estado}")
            print(f"   📋 MensajeError: '{log_record.MensajeError}'")
            
            # Verificar que no sea NULL
            if log_record.MensajeError and log_record.MensajeError != "NULL":
                print(f"   ✅ MensajeError no es NULL: '{log_record.MensajeError}'")
            else:
                print(f"   ❌ MensajeError es NULL o vacío")
                return False
        else:
            print(f"   ❌ Se encontraron {count_logs} registros (debería ser 1)")
            return False
        
        # 3. Probar ejecución de MigrationProcess
        print("\n3️⃣ Probando ejecución de MigrationProcess...")
        
        # Crear conexión y fuente de datos de prueba si no existen
        connection, created = DatabaseConnection.objects.get_or_create(
            name="Conexión Test Logging",
            defaults={
                'server': 'localhost',
                'database': 'test',
                'username': 'test_user',
                'use_windows_auth': True
            }
        )
        
        source, created = DataSource.objects.get_or_create(
            name="Fuente Test Logging",
            defaults={
                'source_type': 'sql',
                'connection': connection
            }
        )
        
        # Crear proceso de migración
        process = MigrationProcess.objects.create(
            name="TEST_LOGGING_UNIFICADO_MIGRATION",
            description="Proceso de prueba para logging unificado",
            source=source,
            selected_tables="tabla_test",
            target_db_name="destino"
        )
        
        print(f"   📦 Proceso creado: {process.name} (ID: {process.id})")
        
        # Ejecutar el proceso (ahora con lógica real)
        try:
            process.run()
            print(f"   ✅ Proceso ejecutado exitosamente")
            
            # Verificar que se insertaron datos en DestinoAutomatizacion
            destino_records = ResultadosProcesados.objects.using('destino').filter(
                Tipo__icontains="TEST_LOGGING_UNIFICADO"
            )
            
            if destino_records.exists():
                record = destino_records.first()
                print(f"   ✅ Datos encontrados en DestinoAutomatizacion:")
                print(f"       ResultadoID: {record.ResultadoID}")
                print(f"       ProcesoID: {record.ProcesoID}")
                print(f"       Estado: {record.Estado}")
                print(f"       Tipo: {record.Tipo}")
            else:
                print(f"   ❌ No se encontraron datos en DestinoAutomatizacion")
                return False
                
        except Exception as e:
            print(f"   ❌ Error ejecutando proceso: {str(e)}")
            return False
        
        print("\n🎯 RESUMEN DE PRUEBAS:")
        print("✅ Solo un registro por proceso en LogsAutomatizacion")
        print("✅ Mensajes presentables (no NULL) en campo errores")
        print("✅ Datos insertados correctamente en DestinoAutomatizacion")
        print("✅ Sistema de logging unificado funcionando correctamente")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error en la prueba: {str(e)}")
        import traceback
        print(traceback.format_exc())
        return False

def verificar_estado_actual():
    """Verificar el estado actual de las bases de datos"""
    
    print("\n" + "=" * 80)
    print("📊 ESTADO ACTUAL DE LAS BASES DE DATOS")
    print("=" * 80)
    
    # LogsAutomatizacion
    try:
        logs_count = ProcesoLog.objects.using('logs').count()
        print(f"\n📋 LogsAutomatizacion: {logs_count} registros")
        
        recent_logs = ProcesoLog.objects.using('logs').order_by('-FechaEjecucion')[:5]
        for log in recent_logs:
            print(f"   🔸 {log.NombreProceso} | {log.Estado} | Error: '{log.MensajeError}'")
            
    except Exception as e:
        print(f"❌ Error accediendo LogsAutomatizacion: {str(e)}")
    
    # DestinoAutomatizacion
    try:
        destino_count = ResultadosProcesados.objects.using('destino').count()
        print(f"\n🎯 DestinoAutomatizacion: {destino_count} registros")
        
        recent_destino = ResultadosProcesados.objects.using('destino').order_by('-ResultadoID')[:5]
        for record in recent_destino:
            print(f"   🔸 ID:{record.ResultadoID} | {record.Estado} | Tipo: {record.Tipo}")
            
    except Exception as e:
        print(f"❌ Error accediendo DestinoAutomatizacion: {str(e)}")

if __name__ == "__main__":
    print("🚀 Iniciando pruebas del sistema de logging unificado...")
    
    # Verificar estado actual
    verificar_estado_actual()
    
    # Ejecutar prueba
    success = test_logging_unificado()
    
    if success:
        print("\n🎉 ¡TODAS LAS PRUEBAS PASARON!")
        print("✅ El sistema de logging unificado está funcionando correctamente")
    else:
        print("\n💥 ALGUNAS PRUEBAS FALLARON")
        print("❌ Revisar la configuración del sistema")
    
    # Verificar estado después de la prueba
    verificar_estado_actual()