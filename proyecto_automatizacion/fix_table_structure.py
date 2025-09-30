#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para verificar y corregir la estructura de la tabla ResultadosProcesados
"""
import pyodbc

def check_and_fix_table():
    """
    Verifica y corrige la estructura de ResultadosProcesados
    """
    try:
        # Conectar a la base de datos
        conn_str = 'DRIVER={ODBC Driver 17 for SQL Server};SERVER=localhost\\SQLEXPRESS;DATABASE=DestinoAutomatizacion;Trusted_Connection=yes;'
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()
        
        print("=== VERIFICANDO ESTRUCTURA DE ResultadosProcesados ===")
        
        # Obtener columnas actuales
        cursor.execute("""
            SELECT COLUMN_NAME
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_NAME = 'ResultadosProcesados'
            ORDER BY ORDINAL_POSITION
        """)
        
        current_columns = [row[0] for row in cursor.fetchall()]
        print(f"Columnas actuales: {current_columns}")
        
        # Columnas esperadas
        expected_columns = [
            'ResultadoID', 'ProcesoID', 'FechaRegistro', 'DatosProcesados', 
            'UsuarioResponsable', 'EstadoProceso', 'TipoOperacion', 
            'RegistrosAfectados', 'TiempoEjecucion', 'MetadatosProceso'
        ]
        
        missing_columns = [col for col in expected_columns if col not in current_columns]
        
        if missing_columns:
            print(f"Columnas faltantes: {missing_columns}")
            print("Agregando columnas...")
            
            for col in missing_columns:
                if col == 'EstadoProceso':
                    cursor.execute("ALTER TABLE ResultadosProcesados ADD EstadoProceso nvarchar(50) DEFAULT 'COMPLETADO'")
                elif col == 'TipoOperacion':
                    cursor.execute("ALTER TABLE ResultadosProcesados ADD TipoOperacion nvarchar(100) NULL")
                elif col == 'RegistrosAfectados':
                    cursor.execute("ALTER TABLE ResultadosProcesados ADD RegistrosAfectados int DEFAULT 0")
                elif col == 'TiempoEjecucion':
                    cursor.execute("ALTER TABLE ResultadosProcesados ADD TiempoEjecucion decimal(10,2) NULL")
                elif col == 'MetadatosProceso':
                    cursor.execute("ALTER TABLE ResultadosProcesados ADD MetadatosProceso ntext NULL")
                
                print(f"✓ Columna {col} agregada")
            
            conn.commit()
            print("🎉 Tabla corregida exitosamente")
        else:
            print("✓ Todas las columnas están presentes")
        
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    check_and_fix_table()
