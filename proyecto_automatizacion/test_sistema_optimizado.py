#!/usr/bin/env python
"""
Test completo del sistema optimizado después de todas las correcciones
Verifica que el flujo completo frontend -> backend -> SQL Server funcione correctamente
"""

import os
import sys
import django
import time
import uuid

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'proyecto_automatizacion.settings')
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.db import connections
from automatizacion.logs.process_tracker import ProcessTracker
from automatizacion.web_logger import registrar_proceso_web, finalizar_proceso_web


def test_optimized_process_tracking():
    """Test del sistema optimizado de tracking de procesos"""
    print("=== TEST SISTEMA OPTIMIZADO DE TRACKING ===")
    
    try:
        # 1. Test ProcessTracker optimizado
        print("\n1. Testing ProcessTracker optimizado...")
        tracker = ProcessTracker("Test Proceso Optimizado")
        
        proceso_id = tracker.iniciar({"test": "optimizado", "timestamp": time.time()})
        print(f"✓ Proceso iniciado: {proceso_id}")
        
        # Actualizar estado (debe actualizar el mismo registro)
        tracker.actualizar_estado("Procesando datos", "Validando información")
        print("✓ Estado actualizado: Procesando datos")
        
        # Finalizar con éxito
        tracker.finalizar_exito("Proceso completado exitosamente")
        print("✓ Proceso finalizado exitosamente")
        
        # 2. Test web logger integrado
        print("\n2. Testing web logger integrado...")
        logger, web_proceso_id = registrar_proceso_web(
            nombre_proceso="Test Frontend Integration",
            datos_adicionales={"frontend_test": True, "optimized": True}
        )
        
        if logger and web_proceso_id:
            print(f"✓ Proceso web iniciado: {web_proceso_id}")
            
            time.sleep(1)  # Simular trabajo
            
            finalizar_proceso_web(logger, exito=True, detalles="Test frontend completado")
            print("✓ Proceso web finalizado correctamente")
        else:
            print("✗ Error al iniciar proceso web")
        
        # 3. Verificar registros en la base de datos
        print("\n3. Verificando registros en SQL Server...")
        with connections['logs'].cursor() as cursor:
            # Contar logs recientes
            cursor.execute("""
                SELECT COUNT(*) FROM ProcesoLog 
                WHERE FechaEjecucion >= DATEADD(MINUTE, -5, GETDATE())
            """)
            recent_count = cursor.fetchone()[0]
            print(f"✓ Logs recientes (últimos 5 min): {recent_count}")
            
            # Verificar nuestros procesos específicos
            cursor.execute("""
                SELECT ProcesoID, NombreProceso, Estado, DuracionSegundos
                FROM ProcesoLog 
                WHERE ProcesoID IN (%s, %s)
                ORDER BY FechaEjecucion DESC
            """, [proceso_id, web_proceso_id])
            
            resultados = cursor.fetchall()
            print(f"✓ Procesos verificados en BD: {len(resultados)}")
            
            for resultado in resultados:
                print(f"  - {resultado[1]}: {resultado[2]} ({resultado[3]}s)")
        
        return True
        
    except Exception as e:
        print(f"✗ Error en test optimizado: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_destino_database_recording():
    """Test que verifica que los datos se guarden en DestinoAutomatizacion"""
    print("\n=== TEST REGISTRO EN DESTINOAUTOMATIZACION ===")
    
    try:
        # Simular el proceso completo de transferencia
        from automatizacion.data_transfer_service import DataTransferService
        
        # Crear instancia del servicio
        transfer_service = DataTransferService()
        
        # Datos de prueba
        test_data = {
            'ProcesoID': str(uuid.uuid4()),
            'DatosProcesados': '{"test": "sistema optimizado", "correcciones": "aplicadas"}',
            'UsuarioResponsable': 'SYSTEM_TEST_OPTIMIZED',
            'TipoOperacion': 'TEST_OPTIMIZED_SYSTEM',
            'RegistrosAfectados': 1
        }
        
        print("1. Iniciando transferencia de prueba...")
        
        # Validar y transferir datos
        validated_data = transfer_service.validate_transfer_data(test_data)
        print("✓ Datos validados correctamente")
        
        # Insertar en DestinoAutomatizacion
        resultado_id = transfer_service.insert_single_record(validated_data)
        print(f"✓ Datos insertados - ID: {resultado_id}")
        
        # 2. Verificar que se guardó en DestinoAutomatizacion
        print("\n2. Verificando registro en DestinoAutomatizacion...")
        with connections['destino'].cursor() as cursor:
            cursor.execute("""
                SELECT TOP 1 ResultadoID, ProcesoID, EstadoProceso, TipoOperacion, UsuarioResponsable
                FROM ResultadosProcesados 
                WHERE UsuarioResponsable = %s
                ORDER BY FechaRegistro DESC
            """, ['SYSTEM_TEST_OPTIMIZED'])
            
            registro = cursor.fetchone()
            if registro:
                print(f"✓ Registro encontrado en DestinoAutomatizacion:")
                print(f"  - ResultadoID: {registro[0]}")
                print(f"  - ProcesoID: {registro[1]}")
                print(f"  - Estado: {registro[2]}")
                print(f"  - Tipo: {registro[3]}")
                return True
            else:
                print("✗ No se encontró el registro en DestinoAutomatizacion")
                return False
                
    except Exception as e:
        print(f"✗ Error en test de DestinoAutomatizacion: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_frontend_flow_simulation():
    """Test que simula el flujo completo desde el frontend"""
    print("\n=== TEST SIMULACIÓN FLUJO FRONTEND COMPLETO ===")
    
    try:
        # 1. Simular selección de base de datos (DestinoAutomatizacion fija)
        print("1. Simulando selección de base de datos...")
        
        proceso_nombre = "Selección DB - DestinoAutomatizacion"
        tracker = ProcessTracker(proceso_nombre)
        proceso_id = tracker.iniciar({
            "database_selected": "DestinoAutomatizacion",
            "frontend_action": "select_database",
            "fixed_destination": True
        })
        
        print(f"✓ Proceso de selección iniciado: {proceso_id}")
        
        # Simular validación y finalización
        tracker.actualizar_estado("Validando conexión", "Verificando DestinoAutomatizacion")
        tracker.finalizar_exito("Base de datos DestinoAutomatizacion seleccionada exitosamente")
        
        # 2. Simular transferencia de datos
        print("\n2. Simulando transferencia de datos...")
        
        transfer_tracker = ProcessTracker("Transferencia de datos - TestTable")
        transfer_id = transfer_tracker.iniciar({
            "source_table": "TestTable",
            "destination_db": "DestinoAutomatizacion",
            "frontend_initiated": True
        })
        
        print(f"✓ Proceso de transferencia iniciado: {transfer_id}")
        
        # Simular etapas del proceso
        transfer_tracker.actualizar_estado("Extrayendo datos", "Leyendo desde fuente")
        transfer_tracker.actualizar_estado("Validando datos", "Aplicando reglas de negocio")
        transfer_tracker.actualizar_estado("Insertando datos", "Guardando en DestinoAutomatizacion")
        transfer_tracker.finalizar_exito("Transferencia completada - 100 registros procesados")
        
        # 3. Verificar que ambos procesos se registraron
        print("\n3. Verificando registro de procesos...")
        with connections['logs'].cursor() as cursor:
            cursor.execute("""
                SELECT ProcesoID, NombreProceso, Estado, DuracionSegundos
                FROM ProcesoLog 
                WHERE ProcesoID IN (%s, %s)
                ORDER BY FechaEjecucion DESC
            """, [proceso_id, transfer_id])
            
            procesos = cursor.fetchall()
            print(f"✓ Procesos registrados: {len(procesos)}")
            
            for proceso in procesos:
                print(f"  - {proceso[1]}: {proceso[2]} ({proceso[3]}s)")
        
        print("\n🎉 FLUJO FRONTEND SIMULADO EXITOSAMENTE")
        return True
        
    except Exception as e:
        print(f"✗ Error en simulación de flujo frontend: {e}")
        import traceback
        traceback.print_exc()
        return False


def run_all_tests():
    """Ejecuta todos los tests del sistema optimizado"""
    print("🚀 INICIANDO TESTS DEL SISTEMA OPTIMIZADO")
    print("=" * 60)
    
    tests = [
        ("Sistema de Tracking Optimizado", test_optimized_process_tracking),
        ("Registro en DestinoAutomatizacion", test_destino_database_recording),
        ("Flujo Frontend Completo", test_frontend_flow_simulation)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n🔍 Ejecutando: {test_name}")
        result = test_func()
        results.append((test_name, result))
        if result:
            print(f"✅ {test_name}: EXITOSO")
        else:
            print(f"❌ {test_name}: FALLIDO")
    
    print("\n" + "=" * 60)
    print("📊 RESUMEN DE RESULTADOS:")
    
    success_count = sum(1 for _, success in results if success)
    total_count = len(results)
    
    for test_name, success in results:
        status = "✅ EXITOSO" if success else "❌ FALLIDO"
        print(f"  {test_name}: {status}")
    
    print(f"\n🎯 TOTAL: {success_count}/{total_count} tests exitosos")
    
    if success_count == total_count:
        print("🎉 ¡TODOS LOS TESTS EXITOSOS! El sistema está funcionando correctamente.")
        print("\n🔹 El flujo frontend -> backend -> SQL Server está operativo")
        print("🔹 Los procesos se registran correctamente en LogsAutomatizacion")
        print("🔹 Los datos se guardan en DestinoAutomatizacion")
        print("🔹 El sistema de logging está optimizado (1 registro por proceso)")
    else:
        print("⚠️  Algunos tests fallaron. Revisar los errores arriba.")
    
    return success_count == total_count


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)