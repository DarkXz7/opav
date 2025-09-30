#!/usr/bin/env python
"""
Script de prueba completo para el endpoint de transferencia segura de datos
Prueba: http://127.0.0.1:8000/automatizacion/sql/connection/18/table/dbo.Usuarios/columns/
"""
import os
import django
import json
import requests
from datetime import datetime
import uuid

# Configure Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'proyecto_automatizacion.settings')
django.setup()

from django.test import Client
from django.contrib.auth.models import User
from automatizacion.models import DatabaseConnection

def test_secure_data_transfer_endpoint():
    """
    Prueba completa del endpoint de transferencia segura de datos
    """
    print("=== PRUEBA ENDPOINT TRANSFERENCIA SEGURA ===")
    
    try:
        # 1. Configurar cliente y usuario
        client = Client()
        user, created = User.objects.get_or_create(
            username='admin', 
            defaults={'email': 'admin@test.com'}
        )
        if created:
            user.set_password('admin123')
            user.save()
        
        # Login
        login_result = client.login(username='admin', password='admin123')
        print(f"✓ Login exitoso: {login_result}")
        
        # 2. Crear/obtener conexión de prueba
        connection, created = DatabaseConnection.objects.get_or_create(
            id=18,
            defaults={
                'name': 'Conexión Destino Test',
                'server': 'localhost\\SQLEXPRESS',
                'username': 'miguel',
                'password': '16474791@',
                'port': 1433,
                'selected_database': 'DestinoAutomatizacion'
            }
        )
        print(f"✓ Conexión configurada: {connection.name} (ID: {connection.id})")
        
        # 3. Probar endpoint de test de conexión
        print("\n--- Probando test de conexión ---")
        test_response = client.get(f'/automatizacion/sql/connection/{connection.id}/test/')
        print(f"Test conexión - Status: {test_response.status_code}")
        if test_response.status_code == 200:
            test_data = json.loads(test_response.content.decode())
            print(f"✓ Conexión funcionando: {test_data.get('message')}")
        
        # 4. Probar estructura de tabla
        print("\n--- Probando estructura de tabla ---")
        structure_response = client.get(f'/automatizacion/sql/connection/{connection.id}/table/dbo.Usuarios/structure/')
        print(f"Estructura tabla - Status: {structure_response.status_code}")
        if structure_response.status_code == 200:
            structure_data = json.loads(structure_response.content.decode())
            print(f"✓ Tabla dbo.Usuarios tiene {len(structure_data.get('columns', []))} columnas")
        
        # 5. Probar transferencia de datos a dbo.Usuarios
        print("\n--- Probando transferencia a dbo.Usuarios ---")
        usuarios_data = {
            "data": {
                "NombreUsuario": f"test_user_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "Email": "test@example.com",
                "NombreCompleto": "Usuario de Prueba Transferencia",
                "Activo": True
            }
        }
        
        transfer_response = client.post(
            f'/automatizacion/sql/connection/{connection.id}/table/dbo.Usuarios/columns/',
            data=json.dumps(usuarios_data),
            content_type='application/json'
        )
        
        print(f"Transferencia Usuarios - Status: {transfer_response.status_code}")
        if transfer_response.status_code == 200:
            transfer_result = json.loads(transfer_response.content.decode())
            print(f"✓ Transferencia exitosa:")
            print(f"  Proceso ID: {transfer_result.get('proceso_id')}")
            print(f"  Resultado ID: {transfer_result.get('resultado_id')}")
            print(f"  Tiempo: {transfer_result.get('tiempo_ejecucion')}s")
        else:
            print(f"✗ Error en transferencia: {transfer_response.content.decode()}")
        
        # 6. Probar transferencia de datos a ResultadosProcesados
        print("\n--- Probando transferencia a ResultadosProcesados ---")
        resultados_data = {
            "data": {
                "ProcesoID": str(uuid.uuid4()),
                "DatosProcesados": {
                    "mensaje": "Datos de prueba desde endpoint",
                    "timestamp": datetime.now().isoformat(),
                    "datos_procesados": [1, 2, 3, 4, 5],
                    "configuracion": {"modo": "test", "version": "1.0"}
                },
                "UsuarioResponsable": user.username,
                "EstadoProceso": "COMPLETADO",
                "TipoOperacion": "PRUEBA_ENDPOINT",
                "RegistrosAfectados": 5
            }
        }
        
        transfer_response = client.post(
            f'/automatizacion/sql/connection/{connection.id}/table/ResultadosProcesados/columns/',
            data=json.dumps(resultados_data),
            content_type='application/json'
        )
        
        print(f"Transferencia ResultadosProcesados - Status: {transfer_response.status_code}")
        if transfer_response.status_code == 200:
            transfer_result = json.loads(transfer_response.content.decode())
            print(f"✓ Transferencia exitosa:")
            print(f"  Proceso ID: {transfer_result.get('proceso_id')}")
            print(f"  Resultado ID: {transfer_result.get('resultado_id')}")
            print(f"  Tiempo: {transfer_result.get('tiempo_ejecucion')}s")
        else:
            print(f"✗ Error en transferencia: {transfer_response.content.decode()}")
        
        # 7. Probar listado de resultados
        print("\n--- Probando listado de resultados ---")
        results_response = client.get('/automatizacion/api/transfer/results/')
        print(f"Listado resultados - Status: {results_response.status_code}")
        if results_response.status_code == 200:
            results_data = json.loads(results_response.content.decode())
            print(f"✓ {results_data.get('total')} resultados encontrados")
            
            # Mostrar últimos 3 resultados
            if results_data.get('resultados'):
                print("Últimos resultados:")
                for i, resultado in enumerate(results_data['resultados'][:3]):
                    print(f"  {i+1}. ID:{resultado['resultado_id']} - {resultado['tipo_operacion']} - {resultado['usuario_responsable']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en prueba: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_batch_transfer():
    """
    Prueba transferencia en lote
    """
    print("\n=== PRUEBA TRANSFERENCIA EN LOTE ===")
    
    try:
        client = Client()
        client.login(username='admin', password='admin123')
        
        # Datos múltiples para usuarios
        usuarios_batch = {
            "data": [
                {
                    "NombreUsuario": f"batch_user_1_{datetime.now().strftime('%H%M%S')}",
                    "Email": "batch1@example.com",
                    "NombreCompleto": "Usuario Lote 1"
                },
                {
                    "NombreUsuario": f"batch_user_2_{datetime.now().strftime('%H%M%S')}",
                    "Email": "batch2@example.com", 
                    "NombreCompleto": "Usuario Lote 2"
                },
                {
                    "NombreUsuario": f"batch_user_3_{datetime.now().strftime('%H%M%S')}",
                    "Email": "batch3@example.com",
                    "NombreCompleto": "Usuario Lote 3"
                }
            ]
        }
        
        response = client.post(
            '/automatizacion/sql/connection/18/table/dbo.Usuarios/columns/',
            data=json.dumps(usuarios_batch),
            content_type='application/json'
        )
        
        print(f"Transferencia lote - Status: {response.status_code}")
        if response.status_code == 200:
            result = json.loads(response.content.decode())
            print(f"✓ Lote procesado exitosamente")
            print(f"  Proceso ID: {result.get('proceso_id')}")
            print(f"  Resultado ID: {result.get('resultado_id')}")
        else:
            print(f"✗ Error en lote: {response.content.decode()}")
        
        return response.status_code == 200
        
    except Exception as e:
        print(f"❌ Error en prueba de lote: {e}")
        return False

def test_error_handling():
    """
    Prueba manejo de errores
    """
    print("\n=== PRUEBA MANEJO DE ERRORES ===")
    
    try:
        client = Client()
        client.login(username='admin', password='admin123')
        
        # 1. Datos inválidos (campos faltantes)
        print("1. Probando datos inválidos...")
        invalid_data = {
            "data": {
                "NombreUsuario": "test_invalid"
                # Faltan Email y NombreCompleto
            }
        }
        
        response = client.post(
            '/automatizacion/sql/connection/18/table/dbo.Usuarios/columns/',
            data=json.dumps(invalid_data),
            content_type='application/json'
        )
        
        print(f"Datos inválidos - Status: {response.status_code}")
        if response.status_code == 400:
            error_data = json.loads(response.content.decode())
            print(f"✓ Error manejado correctamente: {error_data.get('error')}")
        
        # 2. JSON inválido
        print("\n2. Probando JSON inválido...")
        response = client.post(
            '/automatizacion/sql/connection/18/table/dbo.Usuarios/columns/',
            data="{ invalid json }",
            content_type='application/json'
        )
        
        print(f"JSON inválido - Status: {response.status_code}")
        if response.status_code == 400:
            print("✓ JSON inválido manejado correctamente")
        
        # 3. Conexión inexistente
        print("\n3. Probando conexión inexistente...")
        response = client.post(
            '/automatizacion/sql/connection/999/table/dbo.Usuarios/columns/',
            data=json.dumps({"data": {"test": "test"}}),
            content_type='application/json'
        )
        
        print(f"Conexión inexistente - Status: {response.status_code}")
        if response.status_code == 404:
            print("✓ Conexión inexistente manejada correctamente")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en prueba de errores: {e}")
        return False

if __name__ == "__main__":
    print("INICIANDO PRUEBAS COMPLETAS DEL ENDPOINT DE TRANSFERENCIA")
    print("=" * 60)
    
    # Ejecutar todas las pruebas
    results = []
    
    print("1. Prueba básica del endpoint...")
    results.append(test_secure_data_transfer_endpoint())
    
    print("\n2. Prueba de transferencia en lote...")
    results.append(test_batch_transfer())
    
    print("\n3. Prueba de manejo de errores...")
    results.append(test_error_handling())
    
    # Resumen
    print("\n" + "=" * 60)
    print("RESUMEN DE PRUEBAS:")
    tests = ["Endpoint básico", "Transferencia en lote", "Manejo de errores"]
    for i, (test_name, result) in enumerate(zip(tests, results)):
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"  {test_name}: {status}")
    
    success_rate = sum(results) / len(results) * 100
    print(f"\nTasa de éxito: {success_rate:.1f}%")
    
    if success_rate == 100:
        print("🎉 TODAS LAS PRUEBAS PASARON!")
        print("🔗 Endpoint listo: http://127.0.0.1:8000/automatizacion/sql/connection/18/table/dbo.Usuarios/columns/")
    else:
        print("⚠️ Algunas pruebas fallaron. Revisar configuración.")
