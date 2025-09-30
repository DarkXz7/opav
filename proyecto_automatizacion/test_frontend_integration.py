#!/usr/bin/env python
"""
Test del endpoint save_process para verificar la integración completa
"""
import os
import django
import json
import pyodbc
from datetime import datetime

# Configure Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'proyecto_automatizacion.settings')
django.setup()

from django.test import Client
from django.contrib.auth.models import User
from automatizacion.models import DataSource

def test_save_process_endpoint():
    """Test completo del endpoint save_process"""
    print("=== TEST ENDPOINT SAVE_PROCESS ===")
    
    try:
        # Configurar cliente y usuario
        client = Client()
        user, created = User.objects.get_or_create(
            username='testuser', 
            defaults={'email': 'test@test.com'}
        )
        if created:
            user.set_password('testpass')
            user.save()
        
        # Login
        login_result = client.login(username='testuser', password='testpass')
        print(f"Login exitoso: {login_result}")
        
        # Crear DataSource de prueba
        source, created = DataSource.objects.get_or_create(
            name='Test Excel File.xlsx',
            defaults={'source_type': 'excel', 'file_path': '/tmp/test.xlsx'}
        )
        print(f"DataSource: {source.name} (ID: {source.id})")
        
        # Preparar datos para el endpoint
        proceso_nombre = f"Proceso desde Frontend {datetime.now().strftime('%Y%m%d_%H%M%S')}"
        data = {
            'name': proceso_nombre,
            'description': 'Test de integración completa frontend-backend',
            'source_id': source.id,
            'selected_sheets': ['Hoja1', 'Hoja2'],
            'target_db': 'test_database'
        }
        
        print(f"Enviando datos: {proceso_nombre}")
        
        # Obtener CSRF token
        csrf_response = client.get('/automatizacion/')
        csrf_token = csrf_response.cookies.get('csrftoken')
        
        # Enviar petición POST
        response = client.post(
            '/automatizacion/api/save_process/', 
            data=json.dumps(data), 
            content_type='application/json',
            HTTP_X_CSRFTOKEN=csrf_token.value if csrf_token else ''
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            response_data = json.loads(response.content.decode())
            print(f"Response: {response_data}")
            
            # Verificar que se creó el log
            proceso_id = response_data.get('proceso_id')
            if proceso_id:
                print(f"ProcesoID creado: {proceso_id}")
                return verificar_log_creado(proceso_id, proceso_nombre)
            else:
                print("No se recibió proceso_id en la respuesta")
                return False
        else:
            print(f"Error HTTP {response.status_code}: {response.content.decode()}")
            return False
            
    except Exception as e:
        print(f"✗ Error en test: {e}")
        import traceback
        traceback.print_exc()
        return False

def verificar_log_creado(proceso_id, proceso_nombre):
    """Verificar que el log se creó correctamente en SQL Server"""
    try:
        conn_str = 'DRIVER={ODBC Driver 17 for SQL Server};SERVER=localhost\\SQLEXPRESS;DATABASE=LogsAutomatizacion;Trusted_Connection=yes;'
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()
        
        # Buscar el log específico
        cursor.execute("""
            SELECT LogID, ProcesoID, NombreProceso, Estado, FechaEjecucion, DuracionSegundos, ParametrosEntrada
            FROM ProcesoLog 
            WHERE ProcesoID = ?
        """, proceso_id)
        
        row = cursor.fetchone()
        if row:
            print(f"✓ Log encontrado:")
            print(f"  LogID: {row[0]}")
            print(f"  ProcesoID: {row[1]}")
            print(f"  NombreProceso: {row[2]}")
            print(f"  Estado: {row[3]}")
            print(f"  FechaEjecucion: {row[4]}")
            print(f"  DuracionSegundos: {row[5]}")
            print(f"  ParametrosEntrada: {row[6][:100]}..." if row[6] else "  ParametrosEntrada: None")
            
            # Verificar que los campos importantes están poblados
            campos_ok = True
            if not row[1]:  # ProcesoID
                print("  ✗ ProcesoID está vacío")
                campos_ok = False
            if not row[2]:  # NombreProceso
                print("  ✗ NombreProceso está vacío")
                campos_ok = False
            if not row[3]:  # Estado
                print("  ✗ Estado está vacío")
                campos_ok = False
            
            if campos_ok:
                print("  ✓ Todos los campos importantes están poblados")
            else:
                print("  ✗ Algunos campos importantes están vacíos")
            
            cursor.close()
            conn.close()
            return campos_ok
        else:
            print(f"✗ No se encontró log con ProcesoID: {proceso_id}")
            cursor.close()
            conn.close()
            return False
            
    except Exception as e:
        print(f"✗ Error verificando log: {e}")
        return False

if __name__ == "__main__":
    print("INICIANDO TEST DE INTEGRACIÓN FRONTEND")
    print("=" * 50)
    
    resultado = test_save_process_endpoint()
    
    print("\n" + "=" * 50)
    if resultado:
        print("🎉 TEST DE INTEGRACIÓN EXITOSO!")
        print("El endpoint save_process está creando logs correctamente.")
    else:
        print("⚠️ TEST DE INTEGRACIÓN FALLÓ")
        print("Revisar la integración entre frontend y backend.")
