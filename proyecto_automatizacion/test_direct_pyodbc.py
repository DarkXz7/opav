#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Inserción directa con pyodbc para diagnosticar el problema
"""
import pyodbc
import uuid
import json
from datetime import datetime

def test_direct_insert():
    """
    Prueba de inserción directa con pyodbc
    """
    try:
        # Conectar a la base de datos
        conn_str = 'DRIVER={ODBC Driver 17 for SQL Server};SERVER=localhost\\SQLEXPRESS;DATABASE=DestinoAutomatizacion;Trusted_Connection=yes;'
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()
        
        print("=== PRUEBA DE INSERCIÓN DIRECTA CON PYODBC ===")
        
        # Verificar estructura de tabla
        print("Estructura de tabla:")
        cursor.execute("""
            SELECT COLUMN_NAME, DATA_TYPE, IS_NULLABLE, ORDINAL_POSITION
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_NAME = 'ResultadosProcesados'
            ORDER BY ORDINAL_POSITION
        """)
        
        columns = cursor.fetchall()
        for col in columns:
            print(f"  {col[3]}: {col[0]} ({col[1]}) - Nullable: {col[2]}")
        
        # Generar datos de prueba
        proceso_id = str(uuid.uuid4())
        datos_prueba = json.dumps({
            "test": "Prueba PYODBC",
            "timestamp": datetime.now().isoformat()
        })
        
        print(f"\nProcesoID: {proceso_id}")
        print(f"DatosProcesados: {datos_prueba}")
        
        # Insertar usando nombres de columnas explícitos
        insert_query = """
            INSERT INTO ResultadosProcesados (
                ProcesoID, 
                DatosProcesados, 
                UsuarioResponsable,
                EstadoProceso,
                TipoOperacion,
                RegistrosAfectados,
                TiempoEjecucion,
                MetadatosProceso
            )
            OUTPUT INSERTED.ResultadoID
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """
        
        print("\nEjecutando inserción...")
        cursor.execute(insert_query, (
            proceso_id,
            datos_prueba,
            "TEST_USER",
            "PRUEBA",
            "TEST_PYODBC",
            1,
            0.5,
            json.dumps({"test": True})
        ))
        
        result = cursor.fetchone()
        if result:
            resultado_id = result[0]
            print(f"✅ ÉXITO - Registro insertado con ID: {resultado_id}")
            
            # Verificar la inserción
            cursor.execute("SELECT * FROM ResultadosProcesados WHERE ResultadoID = ?", (resultado_id,))
            record = cursor.fetchone()
            print(f"Registro verificado: {record}")
            
            conn.commit()
            return True
        else:
            print("❌ No se pudo obtener el ID del registro")
            return False
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        print(f"Tipo de error: {type(e)}")
        return False
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    test_direct_insert()
