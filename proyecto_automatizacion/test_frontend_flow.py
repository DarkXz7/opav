"""
Script para simular el flujo del frontend y verificar que los logs se guardan correctamente
"""

import os
import django
import json
from django.test import Client
from django.contrib.auth.models import User

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'proyecto_automatizacion.settings')
django.setup()

def test_frontend_flow():
    print("="*60)
    print("PRUEBA DE FLUJO COMPLETO DESDE FRONTEND")
    print("="*60)
    
    # Crear cliente de prueba
    client = Client()
    
    # Crear usuario de prueba si no existe
    user, created = User.objects.get_or_create(
        username='test_user',
        defaults={'email': 'test@example.com', 'is_staff': True}
    )
    if created:
        user.set_password('testpass123')
        user.save()
        print("✓ Usuario de prueba creado")
    
    # Hacer login
    client.login(username='test_user', password='testpass123')
    print("✓ Login realizado")
    
    # Contar registros antes
    import pyodbc
    conn_str = 'DRIVER={ODBC Driver 17 for SQL Server};SERVER=localhost\\SQLEXPRESS;DATABASE=LogsAutomatizacion;Trusted_Connection=yes;'
    conn = pyodbc.connect(conn_str)
    cursor = conn.cursor()
    
    cursor.execute('SELECT COUNT(*) FROM ProcesoLog')
    count_before = cursor.fetchone()[0]
    print(f"Registros antes: {count_before}")
    
    # Simular guardado de proceso desde frontend
    from automatizacion.models import DataSource
    
    # Crear una fuente de datos de prueba
    source = DataSource.objects.create(
        name="Archivo de prueba.xlsx",
        source_type="excel",
        file_path="/tmp/test.xlsx"
    )
    print(f"✓ Fuente de datos creada: {source.id}")
    
    # Datos que típicamente envía el frontend
    frontend_data = {
        'name': 'Migración de Clientes desde Excel',
        'description': 'Proceso para migrar datos de clientes desde archivo Excel a base de datos',
        'source_id': source.id,
        'selected_sheets': ['Hoja1', 'Datos'],
        'selected_columns': {'Hoja1': ['id', 'nombre', 'email']},
        'target_db': 'production'
    }
    
    print(f"Enviando datos del proceso: {frontend_data['name']}")
    
    # Simular la llamada AJAX
    response = client.post(
        '/automatizacion/api/save_process/',
        data=json.dumps(frontend_data),
        content_type='application/json'
    )
    
    print(f"Respuesta del servidor: {response.status_code}")
    if response.status_code == 200:
        response_data = json.loads(response.content)
        print(f"✓ Proceso guardado exitosamente: {response_data}")
        process_id = response_data.get('process_id')
    else:
        print(f"❌ Error: {response.content.decode()}")
        return
    
    # Verificar que se creó el registro en SQL Server
    cursor.execute('SELECT COUNT(*) FROM ProcesoLog')
    count_after = cursor.fetchone()[0]
    new_records = count_after - count_before
    
    print(f"Registros después: {count_after}")
    print(f"Nuevos registros: {new_records}")
    
    if new_records > 0:
        # Obtener el último registro
        cursor.execute('''
            SELECT TOP 1 LogID, ProcesoID, Estado, NombreProceso, DuracionSegundos, ParametrosEntrada 
            FROM ProcesoLog 
            ORDER BY LogID DESC
        ''')
        result = cursor.fetchone()
        
        if result:
            print(f"\n✅ REGISTRO CREADO EXITOSAMENTE:")
            print(f"  LogID: {result[0]}")
            print(f"  ProcesoID: {result[1]}")
            print(f"  Estado: {result[2]}")
            print(f"  NombreProceso: {result[3]}")
            print(f"  Duración: {result[4]}s")
            
            # Verificar que el nombre del proceso coincide
            if result[3] and frontend_data['name'] in result[3]:
                print(f"  ✓ Nombre del proceso coincide con el enviado desde frontend")
            else:
                print(f"  ⚠️ Nombre del proceso no coincide exactamente")
                
            # Mostrar parámetros (limitado para legibilidad)
            params = result[5][:200] + "..." if result[5] and len(result[5]) > 200 else result[5]
            print(f"  Parámetros: {params}")
            
        else:
            print("❌ No se encontró el registro creado")
    else:
        print("❌ No se crearon nuevos registros")
    
    # Limpiar
    source.delete()
    conn.close()
    
    print(f"\n{'='*60}")
    print("PRUEBA COMPLETADA")
    print(f"{'='*60}")

if __name__ == "__main__":
    test_frontend_flow()
