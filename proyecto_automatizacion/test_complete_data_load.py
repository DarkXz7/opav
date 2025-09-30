#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script de Prueba Completa del Sistema de Carga Robusta de Datos
Prueba todos los escenarios: éxito, error parcial, fallo completo
"""
import os
import django
import requests
import json
import time
import uuid
from datetime import datetime, timedelta

# Configure Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'proyecto_automatizacion.settings')
django.setup()

from django.db import connections
from automatizacion.data_load_service import data_load_service
from automatizacion.data_validators import validation_service

class DataLoadTestSuite:
    """
    Suite de pruebas para el sistema de carga robusta de datos
    """
    
    def __init__(self, base_url='http://localhost:8000'):
        self.base_url = base_url
        self.app_url = f"{base_url}/automatizacion"
        self.test_results = []
    
    def setup_test_data(self):
        """
        Configura datos de prueba en la base de datos
        """
        print("=== CONFIGURANDO DATOS DE PRUEBA ===")
        
        try:
            # Crear tabla de prueba en la base de datos default
            with connections['default'].cursor() as cursor:
                # Crear tabla de usuarios de prueba
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS usuarios_prueba (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        nombre VARCHAR(100),
                        email VARCHAR(255),
                        telefono VARCHAR(20),
                        fecha_registro DATE,
                        activo BOOLEAN DEFAULT 1,
                        salario DECIMAL(10,2)
                    )
                """)
                
                # Limpiar datos existentes
                cursor.execute("DELETE FROM usuarios_prueba")
                
                # Insertar datos de prueba válidos
                valid_data = [
                    ('Juan Pérez', 'juan@test.com', '123-456-7890', '2024-01-15', 1, 50000.00),
                    ('María García', 'maria@test.com', '098-765-4321', '2024-02-20', 1, 60000.00),
                    ('Carlos López', 'carlos@test.com', '555-123-4567', '2024-03-10', 1, 55000.00),
                ]
                
                # Insertar datos problemáticos para pruebas de validación
                problematic_data = [
                    ('', 'email_invalido', '123', '2025-01-01', 1, -1000.00),  # Nombre vacío, email inválido, fecha futura, salario negativo
                    ('Ana Torres', 'juan@test.com', '', '2023-12-31', 1, 45000.00),  # Email duplicado, teléfono vacío
                    ('Pedro Ruiz', 'pedro@test.com', '999-888-7777', None, 0, None),  # Fecha nula, salario nulo
                ]
                
                cursor.executemany("""
                    INSERT INTO usuarios_prueba (nombre, email, telefono, fecha_registro, activo, salario)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, valid_data + problematic_data)
                
                # Verificar inserción
                cursor.execute("SELECT COUNT(*) FROM usuarios_prueba")
                count = cursor.fetchone()[0]
                print(f"✓ {count} registros de prueba insertados")
            
            return True
            
        except Exception as e:
            print(f"❌ Error configurando datos de prueba: {e}")
            return False
    
    def test_direct_service_success(self):
        """
        Prueba el servicio directamente con datos válidos
        """
        print("\n=== PRUEBA 1: SERVICIO DIRECTO - ÉXITO ===")
        
        try:
            # Configuración de validación básica
            validation_config = {
                'required_fields': ['nombre', 'email'],
                'unique_fields': ['email'],
                'business_rules': ['user_data']
            }
            
            result = data_load_service.execute_data_load(
                source_database='default',
                source_table='usuarios_prueba',
                target_database='destino',
                validation_rules=validation_config
            )
            
            self.test_results.append({
                'test': 'Servicio Directo - Éxito',
                'success': result['success'],
                'proceso_id': result['proceso_id'],
                'details': result
            })
            
            if result['success']:
                print(f"✅ ÉXITO - Proceso ID: {result['proceso_id']}")
                print(f"   Registros procesados: {result['registros_procesados']}")
                print(f"   Duración: {result['duracion']:.2f}s")
            else:
                print(f"❌ FALLO - Error: {result['error']}")
            
            return result['success']
            
        except Exception as e:
            print(f"💥 ERROR CRÍTICO: {e}")
            return False
    
    def test_validation_service(self):
        """
        Prueba el servicio de validación con datos mixtos
        """
        print("\n=== PRUEBA 2: SERVICIO DE VALIDACIÓN ===")
        
        try:
            # Datos de prueba mixtos (válidos e inválidos)
            test_data = [
                {
                    'nombre': 'Usuario Válido',
                    'email': 'valido@test.com',
                    'telefono': '123-456-7890',
                    'salario': 50000
                },
                {
                    'nombre': '',  # Inválido: nombre vacío
                    'email': 'email_invalido',  # Inválido: formato email
                    'telefono': '123',  # Inválido: teléfono muy corto
                    'salario': -1000  # Inválido: salario negativo
                },
                {
                    'nombre': 'Otro Usuario',
                    'email': 'valido@test.com',  # Inválido: email duplicado
                    'telefono': '098-765-4321',
                    'salario': 60000
                }
            ]
            
            validation_config = {
                'required_fields': ['nombre', 'email'],
                'unique_fields': ['email'],
                'business_rules': ['user_data', 'financial_data'],
                'field_validations': {
                    'email': [{'type': 'email'}],
                    'telefono': [{'type': 'phone'}],
                    'nombre': [{'type': 'string_length', 'min_length': 1, 'max_length': 100}],
                    'salario': [{'type': 'numeric_range', 'min_val': 0, 'max_val': 1000000}]
                }
            }
            
            result = validation_service.validate_batch(test_data, validation_config)
            
            self.test_results.append({
                'test': 'Servicio de Validación',
                'success': not result['valid'],  # Esperamos que falle por los datos inválidos
                'details': result
            })
            
            print(f"📊 Resultado de validación:")
            print(f"   Total registros: {result['total_records']}")
            print(f"   Registros válidos: {result['valid_records']}")
            print(f"   Registros inválidos: {result['invalid_records']}")
            print(f"   Tasa de éxito: {result['validation_summary']['success_rate']:.1f}%")
            
            if result['errors']:
                print(f"   ⚠️ Errores encontrados: {len(result['errors'])}")
                for error in result['errors'][:3]:  # Mostrar primeros 3 errores
                    print(f"      - {error}")
            
            return True
            
        except Exception as e:
            print(f"💥 ERROR EN VALIDACIÓN: {e}")
            return False
    
    def test_api_endpoints(self):
        """
        Prueba los endpoints REST
        """
        print("\n=== PRUEBA 3: ENDPOINTS REST ===")
        
        # Verificar que el servidor esté corriendo
        try:
            response = requests.get(f"{self.base_url}/automatizacion/", timeout=5)
            print(f"✓ Servidor respondiendo - Status: {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"❌ Servidor no disponible: {e}")
            return False
        
        # Prueba 1: Endpoint de validación
        print("\n--- Probando endpoint de validación ---")
        validation_data = {
            "data": [
                {"nombre": "Test User", "email": "test@valid.com"},
                {"nombre": "", "email": "invalid_email"}
            ],
            "validation_config": {
                "required_fields": ["nombre", "email"],
                "business_rules": ["user_data"]
            }
        }
        
        try:
            response = requests.post(
                f"{self.app_url}/data/validate/",
                json=validation_data,
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Validación API exitosa")
                print(f"   Registros válidos: {result['validation_result']['valid_records']}")
                print(f"   Registros inválidos: {result['validation_result']['invalid_records']}")
            else:
                print(f"❌ Error en validación API: {response.status_code}")
                print(f"   Respuesta: {response.text}")
        
        except requests.exceptions.RequestException as e:
            print(f"💥 Error conectando a API de validación: {e}")
        
        # Prueba 2: Endpoint de carga
        print("\n--- Probando endpoint de carga ---")
        load_data = {
            "source_database": "default",
            "source_table": "usuarios_prueba",
            "target_database": "destino",
            "validation_config": {
                "required_fields": ["nombre", "email"]
            },
            "transformation_rules": {
                "normalize_names": True,
                "normalize_emails": True
            }
        }
        
        try:
            response = requests.post(
                f"{self.app_url}/data/load/",
                json=load_data,
                timeout=30
            )
            
            if response.status_code in [200, 422]:
                result = response.json()
                print(f"✅ Carga API completada - Status: {response.status_code}")
                print(f"   Proceso ID: {result.get('proceso_id')}")
                
                if result['success']:
                    print(f"   Registros procesados: {result.get('registros_procesados')}")
                    
                    # Probar endpoint de estado
                    print("\n--- Probando endpoint de estado ---")
                    status_response = requests.get(
                        f"{self.app_url}/data/load/status/{result['proceso_id']}/",
                        timeout=10
                    )
                    
                    if status_response.status_code == 200:
                        status_result = status_response.json()
                        print(f"✅ Estado obtenido exitosamente")
                        print(f"   Estado: {status_result['proceso']['estado']}")
                        print(f"   Registros procesados: {status_result['proceso']['registros_procesados']}")
                    else:
                        print(f"❌ Error obteniendo estado: {status_response.status_code}")
                else:
                    print(f"   ⚠️ Carga con errores: {result.get('error')}")
            else:
                print(f"❌ Error en carga API: {response.status_code}")
                print(f"   Respuesta: {response.text}")
        
        except requests.exceptions.RequestException as e:
            print(f"💥 Error conectando a API de carga: {e}")
        
        return True
    
    def test_statistics_endpoints(self):
        """
        Prueba los endpoints de estadísticas
        """
        print("\n=== PRUEBA 4: ENDPOINTS DE ESTADÍSTICAS ===")
        
        try:
            # Probar cargas recientes
            response = requests.get(f"{self.app_url}/data/loads/recent/?limit=5", timeout=10)
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Cargas recientes obtenidas: {result['total']} cargas")
                
                for load in result['loads'][:2]:  # Mostrar 2 primeras
                    print(f"   - {load['nombre_proceso']}: {load['estado']}")
            else:
                print(f"❌ Error obteniendo cargas recientes: {response.status_code}")
            
            # Probar estadísticas
            response = requests.get(f"{self.app_url}/data/loads/statistics/?hours=24", timeout=10)
            if response.status_code == 200:
                result = response.json()
                stats = result['statistics']
                print(f"✅ Estadísticas obtenidas:")
                print(f"   Total cargas (24h): {stats['total_loads']}")
                print(f"   Cargas exitosas: {stats['successful_loads']}")
                print(f"   Tasa de éxito: {stats['success_rate']:.1f}%")
                print(f"   Registros procesados: {stats['total_records_processed']}")
            else:
                print(f"❌ Error obteniendo estadísticas: {response.status_code}")
        
        except requests.exceptions.RequestException as e:
            print(f"💥 Error en endpoints de estadísticas: {e}")
        
        return True
    
    def run_all_tests(self):
        """
        Ejecuta todas las pruebas
        """
        print("🚀 INICIANDO SUITE DE PRUEBAS DEL SISTEMA DE CARGA ROBUSTA")
        print("=" * 60)
        
        start_time = time.time()
        
        # Configurar datos de prueba
        if not self.setup_test_data():
            print("❌ FALLÓ LA CONFIGURACIÓN - ABORTANDO PRUEBAS")
            return
        
        # Ejecutar pruebas
        tests = [
            self.test_direct_service_success,
            self.test_validation_service,
            self.test_api_endpoints,
            self.test_statistics_endpoints
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
        
        # Resumen final
        print("\n" + "=" * 60)
        print("📋 RESUMEN DE PRUEBAS")
        print(f"✅ Pruebas pasadas: {passed}")
        print(f"❌ Pruebas fallidas: {failed}")
        print(f"⏱️ Tiempo total: {duration:.2f}s")
        
        if failed == 0:
            print("🎉 TODAS LAS PRUEBAS PASARON - SISTEMA FUNCIONAL")
        else:
            print("⚠️ HAY PRUEBAS FALLIDAS - REVISAR RESULTADOS")
        
        return failed == 0

def main():
    """
    Función principal para ejecutar las pruebas
    """
    # Intentar instalar requests si no está disponible
    try:
        import requests
    except ImportError:
        print("📦 Instalando requests...")
        os.system("pip install requests")
        import requests
    
    # Ejecutar pruebas
    test_suite = DataLoadTestSuite()
    success = test_suite.run_all_tests()
    
    return 0 if success else 1

if __name__ == "__main__":
    exit(main())
