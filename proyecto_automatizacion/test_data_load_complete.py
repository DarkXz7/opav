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
from datetime import datetime

# Configure Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'proyecto_automatizacion.settings')
django.setup()

from automatizacion.data_load_service import data_load_service
from automatizacion.data_validators import DataValidators, DataTransformations
from django.db import connections
import pyodbc

class DataLoadTester:
    """
    Tester completo para el sistema de carga de datos
    """
    
    def __init__(self):
        self.base_url = "http://localhost:8000/automatizacion"
        self.test_results = []
    
    def run_all_tests(self):
        """
        Ejecuta todos los tests del sistema
        """
        print("=" * 60)
        print("🧪 INICIANDO PRUEBAS COMPLETAS DEL SISTEMA DE CARGA")
        print("=" * 60)
        
        # 1. Preparar datos de prueba
        self.setup_test_data()
        
        # 2. Probar validación de datos
        self.test_data_validation()
        
        # 3. Probar carga exitosa
        self.test_successful_load()
        
        # 4. Probar carga con errores parciales
        self.test_partial_error_load()
        
        # 5. Probar carga completamente fallida
        self.test_complete_failure_load()
        
        # 6. Probar endpoints REST
        self.test_rest_endpoints()
        
        # 7. Mostrar resumen
        self.show_test_summary()
    
    def setup_test_data(self):
        """
        Crea datos de prueba en SQLite
        """
        print("\n📊 PREPARANDO DATOS DE PRUEBA")
        print("-" * 40)
        
        try:
            with connections['default'].cursor() as cursor:
                # Crear tabla de usuarios de prueba
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS test_usuarios (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        NombreUsuario TEXT NOT NULL,
                        Email TEXT,
                        NombreCompleto TEXT,
                        Activo INTEGER DEFAULT 1,
                        FechaCreacion TEXT
                    )
                """)
                
                # Limpiar datos anteriores
                cursor.execute("DELETE FROM test_usuarios")
                
                # Insertar datos de prueba (exitosos)
                usuarios_exitosos = [
                    ('usuario1', 'usuario1@test.com', 'Usuario Uno', 1, datetime.now().isoformat()),
                    ('usuario2', 'usuario2@test.com', 'Usuario Dos', 1, datetime.now().isoformat()),
                    ('usuario3', 'usuario3@test.com', 'Usuario Tres', 0, datetime.now().isoformat()),
                ]
                
                cursor.executemany("""
                    INSERT INTO test_usuarios (NombreUsuario, Email, NombreCompleto, Activo, FechaCreacion)
                    VALUES (?, ?, ?, ?, ?)
                """, usuarios_exitosos)
                
                # Crear tabla con errores parciales
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS test_usuarios_errores (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        NombreUsuario TEXT,
                        Email TEXT,
                        NombreCompleto TEXT,
                        Activo INTEGER DEFAULT 1
                    )
                """)
                
                cursor.execute("DELETE FROM test_usuarios_errores")
                
                # Datos con algunos errores
                usuarios_con_errores = [
                    ('usuario_ok1', 'ok1@test.com', 'Usuario OK Uno', 1),
                    ('usuario_ok2', 'ok2@test.com', 'Usuario OK Dos', 1),
                    (None, 'sin_nombre@test.com', 'Sin Nombre Usuario', 1),  # Error: nombre nulo
                    ('usuario_email_malo', 'email_invalido', 'Email Malo', 1),  # Error: email inválido
                    ('usuario_ok3', 'ok3@test.com', 'Usuario OK Tres', 1),
                ]
                
                cursor.executemany("""
                    INSERT INTO test_usuarios_errores (NombreUsuario, Email, NombreCompleto, Activo)
                    VALUES (?, ?, ?, ?)
                """, usuarios_con_errores)
                
                # Crear tabla completamente errónea
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS test_tabla_vacia (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        campo TEXT
                    )
                """)
                
                cursor.execute("DELETE FROM test_tabla_vacia")
                # No insertar datos (tabla vacía)
                
            print("✅ Datos de prueba creados exitosamente")
            
        except Exception as e:
            print(f"❌ Error creando datos de prueba: {e}")
    
    def test_data_validation(self):
        """
        Prueba las validaciones de datos
        """
        print("\n🔍 PROBANDO VALIDACIÓN DE DATOS")
        print("-" * 40)
        
        try:
            # Test 1: Validar tabla con datos correctos
            validation_rules = DataValidators.create_user_validation_rules()
            result = data_load_service._validate_source_data('default', 'test_usuarios', validation_rules)
            
            if result['valid'] and result['record_count'] == 3:
                print("✅ Test 1: Validación de datos correctos - EXITOSO")
                self.test_results.append(("Validación datos correctos", True, ""))
            else:
                print("❌ Test 1: Validación de datos correctos - FALLIDO")
                self.test_results.append(("Validación datos correctos", False, str(result)))
            
            # Test 2: Validar tabla vacía
            result_empty = data_load_service._validate_source_data('default', 'test_tabla_vacia', validation_rules)
            
            if not result_empty['valid'] and 'vacía' in result_empty['errors'][0]:
                print("✅ Test 2: Validación tabla vacía - EXITOSO")
                self.test_results.append(("Validación tabla vacía", True, ""))
            else:
                print("❌ Test 2: Validación tabla vacía - FALLIDO")
                self.test_results.append(("Validación tabla vacía", False, str(result_empty)))
            
            # Test 3: Validación de registros individuales
            test_record = {
                'NombreUsuario': 'test_user',
                'Email': 'invalid_email',
                'NombreCompleto': 'Test User'
            }
            
            record_validation = DataValidators.validate_record_against_rules(test_record, validation_rules)
            
            if not record_validation['valid'] and any('Email' in error for error in record_validation['errors']):
                print("✅ Test 3: Validación registro individual - EXITOSO")
                self.test_results.append(("Validación registro individual", True, ""))
            else:
                print("❌ Test 3: Validación registro individual - FALLIDO")
                self.test_results.append(("Validación registro individual", False, str(record_validation)))
            
        except Exception as e:
            print(f"❌ Error en pruebas de validación: {e}")
            self.test_results.append(("Validación general", False, str(e)))
    
    def test_successful_load(self):
        """
        Prueba una carga completamente exitosa
        """
        print("\n✅ PROBANDO CARGA EXITOSA")
        print("-" * 40)
        
        try:
            result = data_load_service.execute_data_load(
                source_database='default',
                source_table='test_usuarios',
                target_database='destino',
                validation_rules=DataValidators.create_user_validation_rules(),
                transform_function=DataTransformations.clean_user_data
            )
            
            if result['success'] and result['registros_procesados'] == 3:
                print(f"✅ Carga exitosa completada")
                print(f"   - ProcesoID: {result['proceso_id']}")
                print(f"   - Registros procesados: {result['registros_procesados']}")
                print(f"   - Duración: {result['duracion']:.2f}s")
                self.test_results.append(("Carga exitosa", True, ""))
            else:
                print(f"❌ Carga exitosa fallida: {result}")
                self.test_results.append(("Carga exitosa", False, str(result)))
                
        except Exception as e:
            print(f"❌ Error en carga exitosa: {e}")
            self.test_results.append(("Carga exitosa", False, str(e)))
    
    def test_partial_error_load(self):
        """
        Prueba carga con errores parciales
        """
        print("\n⚠️ PROBANDO CARGA CON ERRORES PARCIALES")
        print("-" * 40)
        
        try:
            result = data_load_service.execute_data_load(
                source_database='default',
                source_table='test_usuarios_errores',
                target_database='destino',
                validation_rules=DataValidators.create_user_validation_rules(),
                transform_function=DataTransformations.clean_user_data
            )
            
            # En este caso, esperamos que algunos registros se procesen pero otros fallen
            if result['success'] and result['registros_procesados'] >= 3:  # Al menos los 3 buenos
                print(f"✅ Carga parcial manejada correctamente")
                print(f"   - ProcesoID: {result['proceso_id']}")
                print(f"   - Registros procesados: {result['registros_procesados']}")
                print(f"   - Duración: {result['duracion']:.2f}s")
                self.test_results.append(("Carga con errores parciales", True, ""))
            else:
                print(f"❌ Carga parcial no manejada correctamente: {result}")
                self.test_results.append(("Carga con errores parciales", False, str(result)))
                
        except Exception as e:
            print(f"❌ Error en carga parcial: {e}")
            self.test_results.append(("Carga con errores parciales", False, str(e)))
    
    def test_complete_failure_load(self):
        """
        Prueba carga que debe fallar completamente
        """
        print("\n❌ PROBANDO CARGA CON FALLO COMPLETO")
        print("-" * 40)
        
        try:
            result = data_load_service.execute_data_load(
                source_database='default',
                source_table='test_tabla_vacia',
                target_database='destino',
                validation_rules=DataValidators.create_user_validation_rules(),
                transform_function=None
            )
            
            if not result['success'] and 'validación' in result.get('error', '').lower():
                print(f"✅ Fallo completo manejado correctamente")
                print(f"   - ProcesoID: {result['proceso_id']}")
                print(f"   - Error: {result['error']}")
                self.test_results.append(("Fallo completo", True, ""))
            else:
                print(f"❌ Fallo completo no manejado correctamente: {result}")
                self.test_results.append(("Fallo completo", False, str(result)))
                
        except Exception as e:
            print(f"❌ Error en prueba de fallo: {e}")
            self.test_results.append(("Fallo completo", False, str(e)))
    
    def test_rest_endpoints(self):
        """
        Prueba los endpoints REST (requiere servidor corriendo)
        """
        print("\n🌐 PROBANDO ENDPOINTS REST")
        print("-" * 40)
        
        try:
            # Test endpoint de información
            response = requests.get(f"{self.base_url}/data/load/", timeout=5)
            if response.status_code == 200:
                data = response.json()
                print("✅ Endpoint GET /data/load/ - EXITOSO")
                print(f"   - Estadísticas: {data.get('estadisticas_ultimos_7_dias', {})}")
                self.test_results.append(("Endpoint GET info", True, ""))
            else:
                print(f"❌ Endpoint GET /data/load/ - FALLIDO: {response.status_code}")
                self.test_results.append(("Endpoint GET info", False, f"Status: {response.status_code}"))
            
            # Test endpoint de validación
            validation_payload = {
                "source_database": "default",
                "source_table": "test_usuarios",
                "validation_type": "users"
            }
            
            response = requests.post(
                f"{self.base_url}/data/validate/", 
                json=validation_payload,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                print("✅ Endpoint POST /data/validate/ - EXITOSO")
                print(f"   - Recomendación: {data.get('recomendacion', 'N/A')}")
                self.test_results.append(("Endpoint POST validate", True, ""))
            else:
                print(f"❌ Endpoint POST /data/validate/ - FALLIDO: {response.status_code}")
                self.test_results.append(("Endpoint POST validate", False, f"Status: {response.status_code}"))
            
            # Test endpoint de carga
            load_payload = {
                "source_database": "default",
                "source_table": "test_usuarios",
                "validation_type": "users",
                "transformation_type": "users"
            }
            
            response = requests.post(
                f"{self.base_url}/data/load/", 
                json=load_payload,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                print("✅ Endpoint POST /data/load/ - EXITOSO")
                print(f"   - Registros procesados: {data.get('registros_procesados', 'N/A')}")
                self.test_results.append(("Endpoint POST load", True, ""))
            else:
                print(f"❌ Endpoint POST /data/load/ - FALLIDO: {response.status_code}")
                self.test_results.append(("Endpoint POST load", False, f"Status: {response.status_code}"))
                
        except requests.exceptions.RequestException as e:
            print(f"⚠️ No se pudo conectar al servidor Django: {e}")
            print("   Asegúrate de que el servidor esté corriendo con 'python manage.py runserver'")
            self.test_results.append(("Endpoints REST", False, f"Conexión: {str(e)}"))
        except Exception as e:
            print(f"❌ Error en pruebas de endpoints: {e}")
            self.test_results.append(("Endpoints REST", False, str(e)))
    
    def show_test_summary(self):
        """
        Muestra resumen de todas las pruebas
        """
        print("\n" + "=" * 60)
        print("📊 RESUMEN DE PRUEBAS")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for _, passed, _ in self.test_results if passed)
        failed_tests = total_tests - passed_tests
        
        print(f"Total de pruebas: {total_tests}")
        print(f"Pruebas exitosas: {passed_tests}")
        print(f"Pruebas fallidas: {failed_tests}")
        print(f"Porcentaje de éxito: {(passed_tests/total_tests)*100:.1f}%")
        
        print("\nDetalle de pruebas:")
        print("-" * 60)
        
        for test_name, passed, details in self.test_results:
            status = "✅ PASS" if passed else "❌ FAIL"
            print(f"{status} {test_name}")
            if not passed and details:
                print(f"      Detalles: {details[:100]}...")
        
        print("\n" + "=" * 60)
        if failed_tests == 0:
            print("🎉 ¡TODAS LAS PRUEBAS PASARON EXITOSAMENTE!")
            print("✅ Sistema de carga robusto funcionando correctamente")
        else:
            print(f"⚠️ {failed_tests} pruebas fallaron. Revisar implementación.")
        print("=" * 60)

def main():
    """
    Función principal
    """
    tester = DataLoadTester()
    tester.run_all_tests()

if __name__ == "__main__":
    main()
