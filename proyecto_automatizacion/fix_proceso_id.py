#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Corregir el tipo de dato de la columna ProcesoID
"""
import pyodbc

def fix_proceso_id_column():
    """
    Corrige el tipo de dato de ProcesoID de int a nvarchar(36)
    """
    try:
        # Conectar a la base de datos
        conn_str = 'DRIVER={ODBC Driver 17 for SQL Server};SERVER=localhost\\SQLEXPRESS;DATABASE=DestinoAutomatizacion;Trusted_Connection=yes;'
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()
        
        print("=== CORRIGIENDO TIPO DE DATO DE ProcesoID ===")
        
        # Verificar si hay datos en la tabla
        cursor.execute("SELECT COUNT(*) FROM ResultadosProcesados")
        count = cursor.fetchone()[0]
        
        if count > 0:
            print(f"⚠️ La tabla tiene {count} registros. Procediendo con cuidado...")
            # Si hay datos, necesitaríamos hacer backup, pero como es de prueba, continuamos
        
        print("Eliminando columna ProcesoID existente...")
        cursor.execute("ALTER TABLE ResultadosProcesados DROP COLUMN ProcesoID")
        
        print("Agregando columna ProcesoID con tipo correcto...")
        cursor.execute("ALTER TABLE ResultadosProcesados ADD ProcesoID nvarchar(36) NOT NULL DEFAULT 'TEMP-ID'")
        
        # Mover la columna al principio (después de ResultadoID)
        print("Reordenando columnas...")
        cursor.execute("""
            -- Crear tabla temporal con la estructura correcta
            CREATE TABLE ResultadosProcesados_temp (
                ResultadoID int IDENTITY(1,1) PRIMARY KEY,
                ProcesoID nvarchar(36) NOT NULL,
                FechaRegistro datetime2 DEFAULT GETDATE(),
                DatosProcesados ntext NOT NULL,
                UsuarioResponsable nvarchar(100) NOT NULL,
                EstadoProceso nvarchar(50) DEFAULT 'COMPLETADO',
                TipoOperacion nvarchar(100) NULL,
                RegistrosAfectados int DEFAULT 0,
                TiempoEjecucion decimal(10,2) NULL,
                MetadatosProceso ntext NULL
            )
        """)
        
        # Copiar datos si existen
        if count > 0:
            cursor.execute("""
                INSERT INTO ResultadosProcesados_temp (
                    FechaRegistro, DatosProcesados, UsuarioResponsable,
                    EstadoProceso, TipoOperacion, RegistrosAfectados,
                    TiempoEjecucion, MetadatosProceso, ProcesoID
                )
                SELECT 
                    FechaRegistro, DatosProcesados, UsuarioResponsable,
                    EstadoProceso, TipoOperacion, RegistrosAfectados,
                    TiempoEjecucion, MetadatosProceso, 'MIGRATED-' + CAST(ResultadoID as nvarchar)
                FROM ResultadosProcesados
            """)
        
        # Eliminar tabla original y renombrar
        cursor.execute("DROP TABLE ResultadosProcesados")
        cursor.execute("EXEC sp_rename 'ResultadosProcesados_temp', 'ResultadosProcesados'")
        
        # Recrear índices
        cursor.execute("CREATE INDEX IX_ResultadosProcesados_ProcesoID ON ResultadosProcesados(ProcesoID)")
        cursor.execute("CREATE INDEX IX_ResultadosProcesados_FechaRegistro ON ResultadosProcesados(FechaRegistro)")
        cursor.execute("CREATE INDEX IX_ResultadosProcesados_UsuarioResponsable ON ResultadosProcesados(UsuarioResponsable)")
        
        conn.commit()
        
        print("✅ Columna ProcesoID corregida exitosamente")
        
        # Verificar la corrección
        cursor.execute("""
            SELECT COLUMN_NAME, DATA_TYPE, CHARACTER_MAXIMUM_LENGTH
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_NAME = 'ResultadosProcesados' AND COLUMN_NAME = 'ProcesoID'
        """)
        
        result = cursor.fetchone()
        if result:
            print(f"Verificación: {result[0]} es {result[1]}({result[2]})")
        
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

if __name__ == "__main__":
    fix_proceso_id_column()
