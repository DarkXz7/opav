#!/usr/bin/env python
"""
Script para probar los endpoints web del sistema de carga de datos
"""

import requests
import json
import time

def test_web_endpoints():
    """Prueba los endpoints web del sistema"""
    base_url = "http://127.0.0.1:8000/automatizacion"
    
    print("=== Probando Endpoints Web ===")
    
    # Test 1: Endpoint de validación de datos
    print("\n1. Probando endpoint de validación...")
    try:
        validation_data = {
            "source_database": "default",
            "source_table": "TestTable",
            "proceso_nombre": "Validación desde Frontend"
        }
        
        response = requests.post(
            f"{base_url}/data/validate/",
            json=validation_data,
            headers={'Content-Type': 'application/json'},
            timeout=30
        )
        
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"✓ Validación exitosa: {json.dumps(result, indent=2)}")
        else:
            print(f"✗ Error en validación: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"✗ Error de conexión en validación: {e}")
    
    # Test 2: Endpoint de carga de datos
    print("\n2. Probando endpoint de carga de datos...")
    try:
        load_data = {
            "source_database": "default",
            "source_table": "TestTable",
            "proceso_nombre": "Carga desde Frontend Test",
            "parametros_adicionales": {
                "test_frontend": True,
                "timestamp": time.time()
            }
        }
        
        response = requests.post(
            f"{base_url}/data/load/",
            json=load_data,
            headers={'Content-Type': 'application/json'},
            timeout=60
        )
        
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"✓ Carga exitosa: {json.dumps(result, indent=2)}")
            
            # Verificar si se guardaron logs
            if 'proceso_id' in result:
                print(f"✓ Proceso ID generado: {result['proceso_id']}")
        else:
            print(f"✗ Error en carga: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"✗ Error de conexión en carga: {e}")
    
    # Test 3: Endpoint de estado
    print("\n3. Probando endpoint de estado...")
    try:
        response = requests.get(
            f"{base_url}/data/loads/recent/",
            timeout=10
        )
        
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"✓ Estado del sistema: {json.dumps(result, indent=2)}")
        else:
            print(f"✗ Error en estado: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"✗ Error de conexión en estado: {e}")


def check_server_running():
    """Verifica si el servidor Django está ejecutándose"""
    try:
        response = requests.get("http://127.0.0.1:8000/", timeout=5)
        print(f"✓ Servidor Django ejecutándose - Status: {response.status_code}")
        return True
    except requests.exceptions.RequestException:
        print("✗ Servidor Django no está ejecutándose")
        return False


if __name__ == "__main__":
    print("Probando endpoints web del sistema de carga de datos...")
    
    if check_server_running():
        test_web_endpoints()
    else:
        print("Por favor, inicia el servidor Django con: python manage.py runserver")
    
    print("\n=== Pruebas web completadas ===")
