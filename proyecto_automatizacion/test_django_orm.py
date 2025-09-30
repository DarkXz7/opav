#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Prueba simple de inserción con Django ORM
"""
import os
import django
import uuid
import json
from datetime import datetime

# Configure Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'proyecto_automatizacion.settings')
django.setup()

def test_django_insert():
    """
    Prueba de inserción directa con Django ORM
    """
    try:
        from automatizacion.models_destino import ResultadosProcesados
        
        print("=== PRUEBA DE INSERCIÓN CON DJANGO ORM ===")
        
        # Generar datos de prueba
        proceso_id = str(uuid.uuid4())
        datos_prueba = {
            "test": "Prueba ORM Django",
            "timestamp": datetime.now().isoformat()
        }
        
        print(f"ProcesoID: {proceso_id}")
        print(f"Datos: {json.dumps(datos_prueba, indent=2)}")
        
        # Crear el registro
        resultado = ResultadosProcesados(
            ProcesoID=proceso_id,
            DatosProcesados=json.dumps(datos_prueba),
            UsuarioResponsable="TEST_USER",
            EstadoProceso="PRUEBA",
            TipoOperacion="TEST_INSERT",
            RegistrosAfectados=1,
            TiempoEjecucion=0.5,
            MetadatosProceso=json.dumps({"test": True})
        )
        
        # Intentar guardar
        print("Intentando guardar...")
        resultado.save(using='destino')
        
        print(f"✅ ÉXITO - Registro insertado con ID: {resultado.ResultadoID}")
        
        # Verificar la inserción
        print("Verificando inserción...")
        check = ResultadosProcesados.objects.using('destino').get(ResultadoID=resultado.ResultadoID)
        print(f"Verificación: {check}")
        
        return True
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        print(f"Tipo de error: {type(e)}")
        return False

if __name__ == "__main__":
    test_django_insert()
