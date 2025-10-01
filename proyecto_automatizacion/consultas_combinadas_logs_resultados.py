#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Consultas combinadas entre ProcesoLog y ResultadosProcesados
Ejemplos de JOINs para análisis completo de procesos
"""
import os
import django
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Configure Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'proyecto_automatizacion.settings')
django.setup()

def ejecutar_consultas_combinadas():
    """Ejecuta consultas combinadas entre ProcesoLog y ResultadosProcesados"""
    from django.db import connections
    
    print("🔍 CONSULTAS COMBINADAS: ProcesoLog + ResultadosProcesados")
    print("=" * 70)
    
    try:
        # Conexión a logs y destino
        logs_conn = connections['logs']
        destino_conn = connections['destino']
        
        # 1. Vista completa: Histórico + Resumen (JOIN principal)
        print("1️⃣ VISTA COMPLETA: Histórico con Resumen")
        print("-" * 50)
        
        query_vista_completa = """
        SELECT 
            -- Información del Log (ProcesoLog)
            pl.LogID,
            pl.ProcesoID,
            pl.NombreProceso as 'Proceso_Log',
            pl.Estado as 'Estado_Log',
            pl.FechaHora as 'Fecha_Ejecucion',
            pl.MigrationProcessID,
            pl.ParametrosEntrada,
            pl.DetallesSalida,
            
            -- Información del Resumen (ResultadosProcesados)
            rp.ResultadoID,
            rp.NombreProceso as 'Proceso_Resumen',
            rp.FechaRegistro as 'Fecha_Resumen',
            rp.EstadoProceso as 'Estado_Resumen',
            rp.TipoOperacion,
            rp.RegistrosAfectados,
            rp.TiempoEjecucion,
            rp.UsuarioResponsable,
            
            -- Campos calculados
            CASE 
                WHEN rp.ResultadoID IS NOT NULL THEN 'CON_RESUMEN'
                ELSE 'SIN_RESUMEN'
            END as 'Tiene_Resumen',
            
            DATEDIFF(second, pl.FechaHora, rp.FechaRegistro) as 'Diferencia_Segundos'
            
        FROM [LogsAutomatizacion].[dbo].[ProcesoLog] pl
        LEFT JOIN [DestinoAutomatizacion].[dbo].[ResultadosProcesados] rp 
            ON pl.ProcesoID = rp.ProcesoID
        WHERE pl.FechaHora >= DATEADD(day, -7, GETDATE())  -- Últimos 7 días
        ORDER BY pl.FechaHora DESC;
        """
        
        with logs_conn.cursor() as cursor:
            cursor.execute(query_vista_completa)
            resultados = cursor.fetchall()
        
        print(f"📊 Encontrados {len(resultados)} registros en los últimos 7 días")
        print()
        
        if resultados:
            print("🔍 Primeros 5 registros:")
            headers = ['LogID', 'ProcesoID', 'Proceso_Log', 'Estado_Log', 'Fecha_Ejecucion', 
                      'MigrationProcessID', 'ResultadoID', 'Proceso_Resumen', 'Estado_Resumen', 
                      'RegistrosAfectados', 'TiempoEjecucion', 'Tiene_Resumen']
            
            for i, row in enumerate(resultados[:5]):
                print(f"\n📋 Registro {i+1}:")
                print(f"   LogID: {row[0]} | ProcesoID: {row[1][:20]}...")
                print(f"   Proceso: {row[2]} | Estado Log: {row[3]}")
                print(f"   Fecha Ejecución: {row[4]}")
                print(f"   MigrationProcessID: {row[5]}")
                print(f"   ResultadoID: {row[8] if row[8] else 'N/A'}")
                print(f"   Estado Resumen: {row[12] if row[12] else 'N/A'}")
                print(f"   Registros Afectados: {row[15] if row[15] else 'N/A'}")
                print(f"   Tiempo Ejecución: {row[16] if row[16] else 'N/A'}s")
                print(f"   Tiene Resumen: {row[18]}")
        
        # 2. Estadísticas de consistencia
        print("\n\n2️⃣ ESTADÍSTICAS DE CONSISTENCIA")
        print("-" * 40)
        
        query_estadisticas = """
        SELECT 
            COUNT(*) as 'Total_Logs',
            COUNT(rp.ResultadoID) as 'Logs_Con_Resumen',
            COUNT(*) - COUNT(rp.ResultadoID) as 'Logs_Sin_Resumen',
            CAST(COUNT(rp.ResultadoID) * 100.0 / COUNT(*) as DECIMAL(5,2)) as 'Porcentaje_Con_Resumen'
        FROM [LogsAutomatizacion].[dbo].[ProcesoLog] pl
        LEFT JOIN [DestinoAutomatizacion].[dbo].[ResultadosProcesados] rp 
            ON pl.ProcesoID = rp.ProcesoID
        WHERE pl.FechaHora >= DATEADD(day, -30, GETDATE());  -- Últimos 30 días
        """
        
        with logs_conn.cursor() as cursor:
            cursor.execute(query_estadisticas)
            stats = cursor.fetchone()
        
        print(f"📊 Estadísticas (últimos 30 días):")
        print(f"   Total de logs: {stats[0]}")
        print(f"   Logs con resumen: {stats[1]}")
        print(f"   Logs sin resumen: {stats[2]}")
        print(f"   Porcentaje con resumen: {stats[3]}%")
        
        # 3. Procesos por MigrationProcessID con resúmenes
        print("\n\n3️⃣ PROCESOS POR MigrationProcessID CON RESÚMENES")
        print("-" * 55)
        
        query_por_proceso = """
        SELECT 
            pl.MigrationProcessID,
            COUNT(DISTINCT pl.ProcesoID) as 'Total_Ejecuciones',
            COUNT(DISTINCT rp.ResultadoID) as 'Ejecuciones_Con_Resumen',
            SUM(CASE WHEN rp.EstadoProceso = 'COMPLETADO' THEN 1 ELSE 0 END) as 'Exitosas',
            SUM(CASE WHEN rp.EstadoProceso = 'ERROR' THEN 1 ELSE 0 END) as 'Con_Error',
            AVG(rp.RegistrosAfectados) as 'Promedio_Registros',
            AVG(rp.TiempoEjecucion) as 'Promedio_Tiempo',
            MAX(pl.FechaHora) as 'Ultima_Ejecucion'
        FROM [LogsAutomatizacion].[dbo].[ProcesoLog] pl
        LEFT JOIN [DestinoAutomatizacion].[dbo].[ResultadosProcesados] rp 
            ON pl.ProcesoID = rp.ProcesoID
        WHERE pl.MigrationProcessID IS NOT NULL
        GROUP BY pl.MigrationProcessID
        ORDER BY COUNT(DISTINCT pl.ProcesoID) DESC;
        """
        
        with logs_conn.cursor() as cursor:
            cursor.execute(query_por_proceso)
            procesos = cursor.fetchall()
        
        print(f"📊 Encontrados {len(procesos)} procesos únicos:")
        
        for proc in procesos:
            print(f"\n📋 MigrationProcessID: {proc[0]}")
            print(f"   Total ejecuciones: {proc[1]}")
            print(f"   Con resumen: {proc[2]}")
            print(f"   Exitosas: {proc[3] if proc[3] else 0}")
            print(f"   Con error: {proc[4] if proc[4] else 0}")
            print(f"   Promedio registros: {proc[5]:.1f}" if proc[5] else "   Promedio registros: N/A")
            print(f"   Promedio tiempo: {proc[6]:.2f}s" if proc[6] else "   Promedio tiempo: N/A")
            print(f"   Última ejecución: {proc[7]}")
        
        # 4. Detalle completo de procesos recientes con JSON
        print("\n\n4️⃣ DETALLE COMPLETO DE PROCESOS RECIENTES")
        print("-" * 50)
        
        query_detalle = """
        SELECT TOP 3
            pl.ProcesoID,
            pl.NombreProceso,
            pl.FechaHora,
            pl.Estado as EstadoLog,
            rp.EstadoProceso as EstadoResumen,
            rp.RegistrosAfectados,
            rp.TiempoEjecucion,
            rp.DatosProcesados,
            rp.MetadatosProceso
        FROM [LogsAutomatizacion].[dbo].[ProcesoLog] pl
        INNER JOIN [DestinoAutomatizacion].[dbo].[ResultadosProcesados] rp 
            ON pl.ProcesoID = rp.ProcesoID
        WHERE rp.EstadoProceso = 'COMPLETADO'
        ORDER BY pl.FechaHora DESC;
        """
        
        with logs_conn.cursor() as cursor:
            cursor.execute(query_detalle)
            detalles = cursor.fetchall()
        
        print("🔍 Últimos 3 procesos completados con detalles JSON:")
        
        import json
        for i, det in enumerate(detalles):
            print(f"\n📋 Proceso {i+1}:")
            print(f"   ProcesoID: {det[0]}")
            print(f"   Nombre: {det[1]}")
            print(f"   Fecha: {det[2]}")
            print(f"   Estado Log: {det[3]} | Estado Resumen: {det[4]}")
            print(f"   Registros: {det[5]} | Tiempo: {det[6]}s")
            
            # Parsear JSON de datos procesados
            if det[7]:
                try:
                    datos_json = json.loads(det[7])
                    print("   📄 Datos Procesados:")
                    print(f"      Tabla destino: {datos_json.get('tabla_destino', 'N/A')}")
                    print(f"      Campos: {len(datos_json.get('campos_columnas', []))}")
                    print(f"      Registros cargados: {datos_json.get('total_registros_cargados', 'N/A')}")
                except:
                    print("   📄 Datos Procesados: (Error parseando JSON)")
            
            # Parsear JSON de metadatos
            if det[8]:
                try:
                    meta_json = json.loads(det[8])
                    print("   🔧 Metadatos:")
                    print(f"      Versión proceso: {meta_json.get('version_proceso', 'N/A')}")
                    print(f"      Tabla creada: {meta_json.get('tabla_creada', 'N/A')}")
                    print(f"      Duración: {meta_json.get('duracion_segundos', 'N/A')}s")
                except:
                    print("   🔧 Metadatos: (Error parseando JSON)")
        
        return True
        
    except Exception as e:
        print(f"❌ ERROR ejecutando consultas: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def crear_vista_sql_combinada():
    """Crea una vista SQL combinada reutilizable"""
    print("\n\n📋 CREANDO VISTA SQL COMBINADA REUTILIZABLE")
    print("=" * 60)
    
    vista_sql = """
    -- VISTA COMBINADA: VistaProcesoCompleto
    -- Une ProcesoLog con ResultadosProcesados para análisis integral
    
    CREATE VIEW VistaProcesoCompleto AS
    SELECT 
        -- IDs y referencias
        pl.LogID,
        pl.ProcesoID,
        pl.MigrationProcessID,
        rp.ResultadoID,
        
        -- Información básica del proceso
        COALESCE(rp.NombreProceso, pl.NombreProceso) as NombreProceso,
        pl.FechaHora as FechaEjecucion,
        rp.FechaRegistro as FechaResumen,
        
        -- Estados
        pl.Estado as EstadoLog,
        rp.EstadoProceso as EstadoResumen,
        CASE 
            WHEN rp.EstadoProceso = 'COMPLETADO' AND pl.Estado = 'Completado' THEN 'EXITO_COMPLETO'
            WHEN rp.EstadoProceso = 'ERROR' OR pl.Estado = 'Error' THEN 'CON_ERRORES'
            WHEN rp.ResultadoID IS NULL THEN 'SIN_RESUMEN'
            ELSE 'ESTADO_MIXTO'
        END as EstadoConsolidado,
        
        -- Métricas
        rp.RegistrosAfectados,
        rp.TiempoEjecucion,
        rp.TipoOperacion,
        rp.UsuarioResponsable,
        
        -- Información adicional
        pl.ParametrosEntrada,
        pl.DetallesSalida,
        rp.DatosProcesados,
        rp.MetadatosProceso,
        
        -- Flags de control
        CASE WHEN rp.ResultadoID IS NOT NULL THEN 1 ELSE 0 END as TieneResumen,
        CASE WHEN pl.MigrationProcessID IS NOT NULL THEN 1 ELSE 0 END as TieneMigrationProcess,
        
        -- Tiempo entre log y resumen (para detección de problemas)
        DATEDIFF(second, pl.FechaHora, rp.FechaRegistro) as DiferenciaSegundos
        
    FROM [LogsAutomatizacion].[dbo].[ProcesoLog] pl
    LEFT JOIN [DestinoAutomatizacion].[dbo].[ResultadosProcesados] rp 
        ON pl.ProcesoID = rp.ProcesoID
    WHERE pl.FechaHora >= DATEADD(day, -90, GETDATE());  -- Últimos 90 días
    """
    
    print("📄 Script SQL para crear vista combinada:")
    print(vista_sql)
    
    # Ejemplos de uso de la vista
    ejemplos_uso = """
    
    -- EJEMPLOS DE USO DE LA VISTA:
    
    -- 1. Procesos recientes con estado consolidado
    SELECT TOP 10
        ProcesoID,
        NombreProceso,
        FechaEjecucion,
        EstadoConsolidado,
        RegistrosAfectados,
        TiempoEjecucion
    FROM VistaProcesoCompleto
    ORDER BY FechaEjecucion DESC;
    
    -- 2. Procesos sin resumen (posibles problemas)
    SELECT 
        LogID,
        ProcesoID,
        NombreProceso,
        FechaEjecucion,
        EstadoLog
    FROM VistaProcesoCompleto
    WHERE TieneResumen = 0
    ORDER BY FechaEjecucion DESC;
    
    -- 3. Estadísticas por MigrationProcessID
    SELECT 
        MigrationProcessID,
        COUNT(*) as TotalEjecuciones,
        SUM(TieneResumen) as ConResumen,
        SUM(CASE WHEN EstadoConsolidado = 'EXITO_COMPLETO' THEN 1 ELSE 0 END) as Exitosas,
        AVG(RegistrosAfectados) as PromedioRegistros,
        AVG(TiempoEjecucion) as PromedioTiempo,
        MAX(FechaEjecucion) as UltimaEjecucion
    FROM VistaProcesoCompleto
    WHERE MigrationProcessID IS NOT NULL
    GROUP BY MigrationProcessID
    ORDER BY TotalEjecuciones DESC;
    
    -- 4. Procesos con errores y sus detalles
    SELECT 
        ProcesoID,
        NombreProceso,
        FechaEjecucion,
        EstadoLog,
        EstadoResumen,
        DetallesSalida,
        DatosProcesados
    FROM VistaProcesoCompleto
    WHERE EstadoConsolidado = 'CON_ERRORES'
    ORDER BY FechaEjecucion DESC;
    
    -- 5. Análisis de rendimiento
    SELECT 
        NombreProceso,
        COUNT(*) as Ejecuciones,
        AVG(TiempoEjecucion) as TiempoPromedio,
        MIN(TiempoEjecucion) as TiempoMinimo,
        MAX(TiempoEjecucion) as TiempoMaximo,
        SUM(RegistrosAfectados) as TotalRegistros
    FROM VistaProcesoCompleto
    WHERE EstadoConsolidado = 'EXITO_COMPLETO'
    GROUP BY NombreProceso
    HAVING COUNT(*) > 1
    ORDER BY TiempoPromedio DESC;
    """
    
    print("📊 Ejemplos de consultas con la vista:")
    print(ejemplos_uso)

if __name__ == '__main__':
    print("🔍 ANÁLISIS COMBINADO: ProcesoLog + ResultadosProcesados")
    print("=" * 70)
    
    # Ejecutar consultas combinadas
    success = ejecutar_consultas_combinadas()
    
    if success:
        # Mostrar vista SQL reutilizable
        crear_vista_sql_combinada()
        
        print("\n" + "="*70)
        print("🎉 CONSULTAS COMBINADAS COMPLETADAS")
        print("✅ Vista completa del histórico con resúmenes")
        print("✅ Estadísticas de consistencia")
        print("✅ Análisis por MigrationProcessID")
        print("✅ Detalles JSON de procesos recientes")
        print("✅ Vista SQL reutilizable creada")
    else:
        print("\n❌ ERROR EN CONSULTAS COMBINADAS")