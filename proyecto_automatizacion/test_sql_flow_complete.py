#!/usr/bin/env python
"""
Test del flujo completo SQL desde conectar hasta guardar proceso
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
from automatizacion.models import DatabaseConnection, DataSource, MigrationProcess

def test_complete_sql_flow():
    """Test completo del flujo SQL desde conexión hasta guardado"""
    print("=== TEST FLUJO SQL COMPLETO ===")
    
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
        print(f"✓ Login exitoso: {login_result}")
        
        # 1. Simular creación de conexión SQL (como si fuera desde el formulario)
        print("\n1. Creando conexión SQL...")
        connection = DatabaseConnection.objects.create(
            name="Test SQL Connection",
            server="localhost\\SQLEXPRESS",
            username="miguel",
            password="password",
            port=1433,
            selected_database="LogsAutomatizacion",
            available_databases=["LogsAutomatizacion", "master", "tempdb"]
        )
        print(f"✓ Conexión creada: {connection.name} (ID: {connection.id})")
        
        # 2. Simular creación de DataSource (como en select_database)
        print("\n2. Creando DataSource...")
        source = DataSource.objects.create(
            source_type='sql',
            name=f"SQL - {connection.name} - {connection.selected_database}",
            connection=connection
        )
        print(f"✓ DataSource creada: {source.name} (ID: {source.id})")
        
        # 3. Simular guardado de proceso (como desde el frontend)
        print("\n3. Simulando guardado de proceso...")
        proceso_nombre = f"Proceso SQL Test {datetime.now().strftime('%Y%m%d_%H%M%S')}"
        data = {
            'name': proceso_nombre,
            'description': 'Test completo del flujo SQL Server',
            'source_id': source.id,
            'selected_database': connection.selected_database,
            'selected_tables': ['ProcesoLog'],
            'selected_columns': {
                'ProcesoLog': ['LogID', 'ProcesoID', 'NombreProceso', 'Estado']
            },
            'target_db': 'target_database'
        }
        
        print(f"Enviando datos: {data}")
        
        # Simular CSRF
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
            print(f"✓ Proceso guardado: {response_data}")
            
            # 4. Verificar que se guardó en Django
            process = MigrationProcess.objects.get(id=response_data['process_id'])
            print(f"✓ Proceso en Django: {process.name} (Tables: {process.selected_tables})")
            
            # 5. Verificar que se guardó en SQL Server logs
            proceso_uuid = response_data.get('proceso_id')
            if proceso_uuid:
                return verificar_log_sql_server(proceso_uuid, proceso_nombre)
            else:
                print("✗ No se recibió proceso_id UUID")
                return False
        else:
            print(f"✗ Error HTTP {response.status_code}: {response.content.decode()}")
            return False
            
    except Exception as e:
        print(f"✗ Error en test: {e}")
        import traceback
        traceback.print_exc()
        return False

def verificar_log_sql_server(proceso_id, proceso_nombre):
    """Verificar que el log se creó en SQL Server"""
    print(f"\n4. Verificando log en SQL Server para UUID: {proceso_id}")
    try:
        conn_str = 'DRIVER={ODBC Driver 17 for SQL Server};SERVER=localhost\\SQLEXPRESS;DATABASE=LogsAutomatizacion;Trusted_Connection=yes;'
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()
        
        # Buscar el log específico
        cursor.execute("""
            SELECT LogID, ProcesoID, NombreProceso, Estado, FechaEjecucion, ParametrosEntrada
            FROM ProcesoLog 
            WHERE ProcesoID = ?
        """, proceso_id)
        
        row = cursor.fetchone()
        if row:
            print(f"✓ Log encontrado en SQL Server:")
            print(f"  LogID: {row[0]}")
            print(f"  ProcesoID: {row[1]}")
            print(f"  NombreProceso: {row[2]}")
            print(f"  Estado: {row[3]}")
            print(f"  FechaEjecucion: {row[4]}")
            
            # Verificar parámetros
            if row[5]:
                try:
                    params = json.loads(row[5])
                    print(f"  Parámetros incluyen: {list(params.keys())}")
                    if 'selected_tables' in params:
                        print(f"  Tablas seleccionadas: {params.get('selected_tables')}")
                except:
                    print(f"  Parámetros (raw): {row[5][:100]}...")
            
            cursor.close()
            conn.close()
            return True
        else:
            print(f"✗ No se encontró log con ProcesoID: {proceso_id}")
            
            # Buscar logs recientes para debug
            cursor.execute("""
                SELECT TOP 3 LogID, ProcesoID, NombreProceso, Estado 
                FROM ProcesoLog 
                WHERE FechaEjecucion >= DATEADD(MINUTE, -5, GETDATE())
                ORDER BY FechaEjecucion DESC
            """)
            
            print("Logs recientes (últimos 5 minutos):")
            for recent_row in cursor.fetchall():
                print(f"  LogID: {recent_row[0]}, UUID: {recent_row[1][:8]}..., Nombre: {recent_row[2]}")
            
            cursor.close()
            conn.close()
            return False
            
    except Exception as e:
        print(f"✗ Error verificando SQL Server: {e}")
        return False

if __name__ == "__main__":
    print("INICIANDO TEST FLUJO SQL COMPLETO")
    print("=" * 50)
    
    resultado = test_complete_sql_flow()
    
    print("\n" + "=" * 50)
    if resultado:
        print("🎉 TEST FLUJO SQL EXITOSO!")
        print("El flujo completo SQL→Django→Logs funciona correctamente.")
    else:
        print("⚠️ TEST FLUJO SQL FALLÓ")
        print("Revisar la integración del flujo SQL completo.")
