from django.db import models
import json
from django.utils import timezone

class DataSourceType(models.Model):
    """
    Define el tipo de origen de datos (Excel, CSV, SQL Server)
    """
    name = models.CharField(max_length=50)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

class DatabaseConnection(models.Model):
    """
    Almacena información de conexión a servidor de base de datos
    """
    name = models.CharField(max_length=100)
    server = models.CharField(max_length=255)
    username = models.CharField(max_length=100)
    password = models.CharField(max_length=255)
    port = models.IntegerField(default=1433)
    created_at = models.DateTimeField(auto_now_add=True)
    last_used = models.DateTimeField(null=True, blank=True)
    selected_database = models.CharField(max_length=100, blank=True, null=True)
    
    # Campo para almacenar todas las bases de datos disponibles
    available_databases = models.JSONField(null=True, blank=True)
    
    def __str__(self):
        if self.selected_database:
            return f"{self.name} - {self.server}/{self.selected_database}"
        return f"{self.name} - {self.server}"
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'server': self.server,
            'selected_database': self.selected_database,
            'username': self.username,
            'password': self.password,
            'port': self.port,
            'available_databases': self.available_databases or []
        }

class DataSource(models.Model):
    """
    Representa una fuente de datos (archivo o conexión a BD)
    """
    TYPE_CHOICES = [
        ('excel', 'Excel (.xlsx)'),
        ('csv', 'CSV'),
        ('sql', 'SQL Server'),
    ]
    
    name = models.CharField(max_length=255)
    source_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    file_path = models.CharField(max_length=255, blank=True, null=True)  # Solo para archivos
    connection = models.ForeignKey(DatabaseConnection, on_delete=models.SET_NULL, null=True, blank=True)  # Solo para SQL
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.name} ({self.get_source_type_display()})"

class MigrationProcess(models.Model):
    """
    Representa un proceso completo de migración guardado
    """
    STATUS_CHOICES = [
        ('draft', 'Borrador'),
        ('db_selected', 'Base de datos seleccionada'),
        ('tables_selected', 'Tablas seleccionadas'),
        ('columns_selected', 'Columnas seleccionadas'),
        ('configured', 'Configurado'),
        ('validated', 'Validado'),
        ('ready', 'Listo para ejecutar'),
        ('running', 'En ejecución'),
        ('completed', 'Completado'),
        ('failed', 'Fallido'),
    ]
    
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    source = models.ForeignKey(DataSource, on_delete=models.CASCADE, related_name='processes')
    
    # Para archivos Excel/CSV
    selected_sheets = models.JSONField(null=True, blank=True)  # Lista de hojas seleccionadas
    
    # Para SQL Server
    selected_database = models.CharField(max_length=100, blank=True, null=True)  # Base de datos seleccionada
    selected_tables = models.JSONField(null=True, blank=True)  # Lista de tablas seleccionadas
    
    # Campos compartidos
    selected_columns = models.JSONField(null=True, blank=True)  # Dict de columnas seleccionadas por tabla/hoja
    
    # Destino de datos
    target_db_name = models.CharField(max_length=100, default='default')
    target_db_connection = models.ForeignKey(DatabaseConnection, on_delete=models.SET_NULL, null=True, blank=True, related_name='target_processes')
    target_table = models.CharField(max_length=100, blank=True, null=True)  # Tabla de destino
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    created_at = models.DateTimeField(auto_now_add=True)
    last_run = models.DateTimeField(null=True, blank=True)
    
    # Opciones de rollback y checkpoint
    allow_rollback = models.BooleanField(default=True)
    last_checkpoint = models.JSONField(null=True, blank=True)  # Para almacenar puntos de restauración
    
    def __str__(self):
        return self.name
    
    def run(self):
        """
        Ejecuta el proceso de migración guardado - PROCESA DATOS REALES DEL ORIGEN
        """
        from .data_transfer_service import data_transfer_service
        import json
        import uuid
        
        self.status = 'running'
        self.last_run = timezone.now()
        self.save()
        
        try:
            # Generar un proceso_id único para esta ejecución
            proceso_id = str(uuid.uuid4())
            
            # Obtener datos reales del origen según el tipo de fuente
            tiempo_inicio = timezone.now()
            datos_origen = self._extract_source_data()
            tiempo_fin = timezone.now()
            duracion_extraccion = (tiempo_fin - tiempo_inicio).total_seconds()
            
            # Calcular estadísticas de los datos extraídos
            registros_procesados = len(datos_origen) if isinstance(datos_origen, list) else 1
            
            # Crear resumen de los datos procesados (NO los datos completos)
            resumen_procesamiento = self._crear_resumen_datos(
                datos_origen, 
                duracion_extraccion, 
                registros_procesados
            )
            
            # Preparar metadatos del proceso
            metadata = {
                'migration_process_id': self.id,
                'process_name': self.name,
                'source_type': self.source.source_type if self.source else 'unknown',
                'source_id': self.source.id if self.source else None,
                'execution_timestamp': tiempo_inicio.isoformat(),
                'selected_tables': self.selected_tables,
                'selected_sheets': self.selected_sheets,
                'selected_columns': self.selected_columns,
                'target_db_name': self.target_db_name,
                'extraction_duration_seconds': duracion_extraccion
            }
            
            # Insertar el RESUMEN (no los datos completos) en tabla dinámica específica del proceso
            success, result_info = data_transfer_service.transfer_to_dynamic_table(
                process_name=self.name,
                proceso_id=proceso_id,
                datos_procesados=resumen_procesamiento,
                usuario_responsable='sistema_automatizado',
                metadata=metadata,
                recreate_table=True,  # Cada ejecución limpia y recrea los datos
                estado_proceso='COMPLETADO',
                tipo_operacion=f'MIGRACION_{self.name.upper().replace(" ", "_")}',
                registros_afectados=registros_procesados
            )
            
            if success:
                self.status = 'completed'
                table_name = result_info.get('table_name', 'Desconocida')
                resultado_id = result_info.get('resultado_id', 'N/A')
                print(f"✅ Proceso '{self.name}' ejecutado exitosamente.")
                print(f"   📋 Tabla específica: '{table_name}'")
                print(f"   📊 Registros procesados: {registros_procesados}")
                print(f"   🆔 ResultadoID: {resultado_id}")
            else:
                self.status = 'failed'
                error_msg = result_info.get('error', 'Error desconocido')
                table_name = result_info.get('table_name', 'No determinada')
                raise Exception(f"Error en transferencia a tabla '{table_name}': {error_msg}")
                
        except Exception as e:
            self.status = 'failed'
            print(f"❌ Error ejecutando proceso {self.name}: {str(e)}")
            raise e
        finally:
            self.save()
    
    def _crear_resumen_datos(self, datos_origen, duracion_extraccion, registros_procesados):
        """
        Crea un resumen JSON de los datos procesados en lugar de guardar todos los datos
        
        Returns:
            dict: Resumen estructurado del procesamiento
        """
        try:
            resumen = {
                'proceso_ejecutado': self.name,
                'timestamp_ejecucion': timezone.now().isoformat(),
                'estadisticas': {
                    'total_registros': registros_procesados,
                    'duracion_extraccion_segundos': round(duracion_extraccion, 2),
                    'tipo_fuente': self.source.source_type if self.source else 'unknown'
                },
                'configuracion': {
                    'tablas_seleccionadas': self.selected_tables,
                    'hojas_seleccionadas': self.selected_sheets,
                    'columnas_seleccionadas': self.selected_columns,
                    'base_datos_destino': self.target_db_name or 'DestinoAutomatizacion'
                }
            }
            
            # Agregar información específica según el tipo de datos
            if isinstance(datos_origen, list):
                if len(datos_origen) > 0:
                    # Muestra de las primeras columnas/campos encontrados (sin datos sensibles)
                    primer_registro = datos_origen[0] if datos_origen else {}
                    if isinstance(primer_registro, dict):
                        resumen['estructura_datos'] = {
                            'columnas_detectadas': list(primer_registro.keys()),
                            'numero_columnas': len(primer_registro.keys()),
                            'muestra_primer_registro': {k: str(v)[:50] + '...' if len(str(v)) > 50 else str(v) 
                                                     for k, v in list(primer_registro.items())[:3]}
                        }
                
                resumen['estadisticas']['registros_validos'] = len([r for r in datos_origen if not (isinstance(r, dict) and r.get('error'))])
                resumen['estadisticas']['registros_con_error'] = len([r for r in datos_origen if isinstance(r, dict) and r.get('error')])
            
            elif isinstance(datos_origen, dict):
                if datos_origen.get('error'):
                    resumen['error_extraccion'] = datos_origen['error']
                    resumen['estadisticas']['extracion_exitosa'] = False
                else:
                    resumen['estadisticas']['extracion_exitosa'] = True
                    # Incluir keys del diccionario pero no valores completos
                    resumen['estructura_datos'] = {
                        'campos_principales': list(datos_origen.keys())[:10]
                    }
            
            # Agregar información de rendimiento
            if registros_procesados > 0 and duracion_extraccion > 0:
                resumen['rendimiento'] = {
                    'registros_por_segundo': round(registros_procesados / duracion_extraccion, 2)
                }
            
            return resumen
            
        except Exception as e:
            # En caso de error creando el resumen, devolver un resumen básico
            return {
                'proceso_ejecutado': self.name,
                'error_creando_resumen': str(e),
                'timestamp_ejecucion': timezone.now().isoformat(),
                'registros_procesados': registros_procesados,
                'duracion_extraccion_segundos': duracion_extraccion
            }
    
    def _extract_source_data(self):
        """
        Extrae datos reales de la fuente configurada (Excel, CSV o SQL)
        
        Returns:
            list|dict: Datos extraídos de la fuente
        """
        if not self.source:
            return {
                'error': 'No hay fuente configurada',
                'proceso': self.name,
                'timestamp': timezone.now().isoformat()
            }
        
        try:
            if self.source.source_type == 'excel':
                return self._extract_excel_data()
            elif self.source.source_type == 'csv':
                return self._extract_csv_data()
            elif self.source.source_type == 'sql':
                return self._extract_sql_data()
            else:
                return {
                    'error': f'Tipo de fuente no soportado: {self.source.source_type}',
                    'proceso': self.name,
                    'timestamp': timezone.now().isoformat()
                }
        except Exception as e:
            return {
                'error': f'Error extrayendo datos: {str(e)}',
                'proceso': self.name,
                'source_type': self.source.source_type,
                'timestamp': timezone.now().isoformat()
            }
    
    def _extract_excel_data(self):
        """Extrae datos de archivo Excel"""
        import pandas as pd
        import json
        
        try:
            if not self.source.file_path:
                return {'error': 'No hay archivo Excel configurado'}
            
            # Obtener hojas seleccionadas
            selected_sheets = json.loads(self.selected_sheets) if self.selected_sheets else []
            if not selected_sheets:
                return {'error': 'No hay hojas seleccionadas'}
            
            data = []
            for sheet_name in selected_sheets:
                df = pd.read_excel(self.source.file_path, sheet_name=sheet_name)
                
                # Filtrar columnas si están especificadas
                if self.selected_columns:
                    selected_cols = json.loads(self.selected_columns).get(sheet_name, [])
                    if selected_cols:
                        df = df[selected_cols]
                
                # Convertir a diccionarios
                sheet_data = df.to_dict('records')
                data.extend([{
                    'sheet': sheet_name,
                    'row_index': idx,
                    **row
                } for idx, row in enumerate(sheet_data)])
            
            return data
            
        except Exception as e:
            return {'error': f'Error procesando Excel: {str(e)}'}
    
    def _extract_csv_data(self):
        """Extrae datos de archivo CSV"""
        import pandas as pd
        import json
        
        try:
            if not self.source.file_path:
                return {'error': 'No hay archivo CSV configurado'}
            
            df = pd.read_csv(self.source.file_path)
            
            # Filtrar columnas si están especificadas
            if self.selected_columns:
                selected_cols = json.loads(self.selected_columns)
                if isinstance(selected_cols, list) and selected_cols:
                    df = df[selected_cols]
            
            # Convertir a diccionarios
            data = df.to_dict('records')
            return [{'row_index': idx, **row} for idx, row in enumerate(data)]
            
        except Exception as e:
            return {'error': f'Error procesando CSV: {str(e)}'}
    
    def _extract_sql_data(self):
        """Extrae datos de base de datos SQL"""
        from .utils import SQLServerConnector
        import json
        
        try:
            if not self.source.connection:
                return {'error': 'No hay conexión SQL configurada'}
            
            # Obtener tablas seleccionadas
            selected_tables = json.loads(self.selected_tables) if self.selected_tables else []
            if not selected_tables:
                return {'error': 'No hay tablas seleccionadas'}
            
            connection = self.source.connection
            connector = SQLServerConnector(
                connection.server,
                connection.username,
                connection.password,
                connection.port
            )
            
            # Conectar a la base de datos
            if not connector.select_database(connection.selected_database):
                return {'error': f'No se pudo conectar a la base de datos {connection.selected_database}'}
            
            all_data = []
            
            for table_info in selected_tables:
                table_name = table_info.get('name') or table_info.get('full_name', '')
                if not table_name:
                    continue
                
                # Obtener datos de la tabla
                try:
                    cursor = connector.conn.cursor()
                    
                    # Construir consulta SELECT
                    if self.selected_columns:
                        selected_cols = json.loads(self.selected_columns).get(table_name, [])
                        if selected_cols:
                            columns = ', '.join([f'[{col}]' for col in selected_cols])
                            query = f"SELECT {columns} FROM [{table_name}]"
                        else:
                            query = f"SELECT * FROM [{table_name}]"
                    else:
                        query = f"SELECT * FROM [{table_name}]"
                    
                    cursor.execute(query)
                    
                    # Obtener nombres de columnas
                    column_names = [column[0] for column in cursor.description]
                    
                    # Obtener datos
                    rows = cursor.fetchall()
                    
                    # Convertir a diccionarios
                    table_data = []
                    for row_idx, row in enumerate(rows):
                        row_dict = {
                            'table_name': table_name,
                            'row_index': row_idx
                        }
                        for col_idx, value in enumerate(row):
                            row_dict[column_names[col_idx]] = value
                        table_data.append(row_dict)
                    
                    all_data.extend(table_data)
                    
                except Exception as table_error:
                    # Agregar error pero continuar con otras tablas
                    all_data.append({
                        'table_name': table_name,
                        'error': f'Error procesando tabla: {str(table_error)}'
                    })
            
            return all_data
            
        except Exception as e:
            return {'error': f'Error procesando SQL: {str(e)}'}
        finally:
            try:
                connector.disconnect()
            except:
                pass
    
    def to_dict(self):
        """
        Convierte el proceso a un diccionario para facilitar la serialización
        """
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'source_type': self.source.source_type,
            'source_id': self.source.id,
            'selected_sheets': self.selected_sheets,
            'selected_tables': self.selected_tables,
            'selected_columns': self.selected_columns,
            'target_db_name': self.target_db_name,
            'status': self.status,
            'created_at': self.created_at.isoformat(),
            'last_run': self.last_run.isoformat() if self.last_run else None
        }

class MigrationLog(models.Model):
    """
    Registra eventos y resultados de cada ejecución del proceso de migración
    """
    LOG_LEVELS = [
        ('info', 'Información'),
        ('warning', 'Advertencia'),
        ('error', 'Error'),
        ('critical', 'Crítico'),
        ('success', 'Éxito'),
        ('debug', 'Depuración')
    ]
    
    LOG_STAGES = [
        ('connection', 'Conexión'),
        ('database_list', 'Listar bases de datos'),
        ('database_select', 'Selección de base de datos'),
        ('table_list', 'Listar tablas'),
        ('table_select', 'Selección de tablas'),
        ('column_list', 'Listar columnas'),
        ('column_select', 'Selección de columnas'),
        ('validation', 'Validación'),
        ('data_extraction', 'Extracción de datos'),
        ('data_transformation', 'Transformación de datos'),
        ('data_loading', 'Carga de datos'),
        ('rollback', 'Rollback'),
        ('completion', 'Finalización')
    ]
    
    process = models.ForeignKey(MigrationProcess, on_delete=models.CASCADE, related_name='logs')
    timestamp = models.DateTimeField(auto_now_add=True)
    stage = models.CharField(max_length=30, choices=LOG_STAGES)
    level = models.CharField(max_length=20, choices=LOG_LEVELS, default='info')
    message = models.TextField()
    rows_processed = models.IntegerField(default=0)
    duration_ms = models.IntegerField(default=0)
    error_message = models.TextField(blank=True, null=True)
    details = models.JSONField(null=True, blank=True)
    user = models.CharField(max_length=100, blank=True, null=True)  # Para registrar qué usuario realizó la acción
    
    def __str__(self):
        return f"Log {self.id} - {self.process.name} - {self.stage} - {self.level}"
    
    @classmethod
    def log(cls, process, stage, message, level='info', rows=0, duration=0, error=None, details=None, user=None):
        """
        Método de clase para crear un nuevo registro de log
        """
        return cls.objects.create(
            process=process,
            stage=stage,
            message=message,
            level=level,
            rows_processed=rows,
            duration_ms=duration,
            error_message=error,
            details=details or {},
            user=user
        )
        
    def complete_log(self, stage, message=None, rows_processed=0, duration_ms=0, error_message=None):
        """
        Actualiza un registro de log existente con información de finalización
        """
        self.stage = stage
        if message:
            self.message = message
        self.rows_processed = rows_processed
        self.duration_ms = duration_ms
        self.error_message = error_message
        self.save()
        return self