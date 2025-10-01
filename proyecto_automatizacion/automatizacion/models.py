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
        ✅ CORREGIDO: Usa ProcessTracker para generar IDs consistentes entre ProcesoLog y tabla dinámica
        """
        from .data_transfer_service import data_transfer_service
        from .logs.process_tracker import ProcessTracker
        import json
        
        self.status = 'running'
        self.last_run = timezone.now()
        self.save()
        
        # CORRECCIÓN 1: Usar ProcessTracker para generar UUID único y crear log en ProcesoLog
        tracker = ProcessTracker(self.name)
        
        try:
            # CORRECCIÓN 2: Iniciar tracking con MigrationProcessID para relación correcta
            parametros_proceso = {
                'migration_process_id': self.id,  # FK al proceso configurado
                'source_type': self.source.source_type if self.source else 'unknown',
                'source_id': self.source.id if self.source else None,
                'selected_tables': self.selected_tables,
                'selected_sheets': self.selected_sheets,
                'selected_columns': self.selected_columns,
                'target_db_name': self.target_db_name
            }
            
            # Iniciar proceso y obtener UUID que se usará en ambas bases de datos
            proceso_id = tracker.iniciar(parametros_proceso)
            
            # NUEVA LÓGICA: Procesar según tipo de fuente
            tiempo_inicio = timezone.now()
            
            if self.source.source_type == 'excel':
                # EXCEL: Procesar cada hoja por separado con tabla independiente
                success, result_info = self._process_excel_sheets_individually(tracker, proceso_id, tiempo_inicio, parametros_proceso)
            else:
                # SQL/CSV: Usar lógica original (una sola tabla)
                datos_origen = self._extract_source_data()
                tiempo_fin = timezone.now()
                duracion_extraccion = (tiempo_fin - tiempo_inicio).total_seconds()
                
                # Calcular estadísticas de los datos extraídos
                registros_procesados = len(datos_origen) if isinstance(datos_origen, list) else 1
                
                # Actualizar estado del proceso
                tracker.actualizar_estado('PROCESANDO_DATOS', 
                    f'Extrayendo {registros_procesados} registros de {self.source.source_type if self.source else "origen"}')
                
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
                
                # Actualizar estado antes de transferencia
                tracker.actualizar_estado('TRANSFIRIENDO', 'Insertando datos en tabla dinámica')
                
                # CORRECCIÓN 3: Usar el mismo proceso_id del tracker en la transferencia
                success, result_info = data_transfer_service.transfer_to_dynamic_table(
                    process_name=self.name,
                    proceso_id=proceso_id,  # ✅ Mismo UUID generado por ProcessTracker
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
                
                # Manejo diferente según tipo de proceso
                if result_info.get('process_type') == 'excel_multi_sheet':
                    # EXCEL: Múltiples hojas procesadas
                    hojas_exitosas = result_info.get('hojas_procesadas', 0)
                    total_registros = result_info.get('total_registros', 0)
                    duracion_total = result_info.get('duracion_total', 0)
                    
                    detalles_exito = f"Excel procesado: {hojas_exitosas} hojas exitosas, {total_registros} registros totales, {duracion_total:.2f}s"
                    tracker.finalizar_exito(detalles_exito)
                    
                    print(f"✅ Proceso Excel '{self.name}' ejecutado exitosamente.")
                    print(f"   📋 Hojas procesadas: {hojas_exitosas}")
                    print(f"   📊 Total registros: {total_registros}")
                    print(f"   ⏱️ Duración total: {duracion_total:.2f}s")
                    print(f"   🔗 ProcesoID principal: {proceso_id}")
                    
                    # Mostrar detalle de cada hoja
                    for hoja in result_info.get('detalles_hojas_exitosas', []):
                        print(f"      🍃 Hoja '{hoja['sheet_name']}': {hoja['registros']} registros → Tabla '{hoja['table_name']}'")
                else:
                    # SQL/CSV: Una sola tabla
                    table_name = result_info.get('table_name', 'Desconocida')
                    resultado_id = result_info.get('resultado_id', 'N/A')
                    registros_procesados = len(datos_origen) if 'datos_origen' in locals() and isinstance(datos_origen, list) else 1
                    
                    detalles_exito = f"Tabla: {table_name}, ResultadoID: {resultado_id}, Registros: {registros_procesados}"
                    tracker.finalizar_exito(detalles_exito)
                    
                    print(f"✅ Proceso '{self.name}' ejecutado exitosamente.")
                    print(f"   📋 Tabla específica: '{table_name}'")
                    print(f"   📊 Registros procesados: {registros_procesados}")
                    print(f"   🆔 ResultadoID: {resultado_id}")
                    print(f"   🔗 ProcesoID (consistente): {proceso_id}")
            else:
                self.status = 'failed'
                
                # Manejo de errores diferente según tipo
                if result_info.get('process_type') == 'excel_multi_sheet_error':
                    # Error en Excel
                    error_msg = result_info.get('error', 'Error desconocido procesando Excel')
                    hojas_fallidas = result_info.get('hojas_con_error', 0)
                    error_completo = f"Error procesando Excel '{self.name}': {error_msg}, {hojas_fallidas} hojas fallaron"
                else:
                    # Error en SQL/CSV
                    error_msg = result_info.get('error', 'Error desconocido')
                    table_name = result_info.get('table_name', 'No determinada')
                    error_completo = f"Error en transferencia a tabla '{table_name}': {error_msg}"
                
                # CORRECCIÓN 5: Registrar error en ProcessTracker antes de lanzar excepción
                tracker.finalizar_error(Exception(error_completo))
                raise Exception(error_completo)
                
        except Exception as e:
            self.status = 'failed'
            # CORRECCIÓN 6: Asegurar que el error se registre en ProcesoLog
            if 'tracker' in locals():
                tracker.finalizar_error(e)
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
            selected_sheets = self.selected_sheets if isinstance(self.selected_sheets, list) else (json.loads(self.selected_sheets) if self.selected_sheets else [])
            if not selected_sheets:
                return {'error': 'No hay hojas seleccionadas'}
            
            data = []
            for sheet_name in selected_sheets:
                df = pd.read_excel(self.source.file_path, sheet_name=sheet_name)
                
                # Filtrar columnas si están especificadas
                if self.selected_columns:
                    selected_cols = (self.selected_columns.get(sheet_name, []) if isinstance(self.selected_columns, dict) else json.loads(self.selected_columns).get(sheet_name, [])) if self.selected_columns else []
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
    
    def _process_excel_sheets_individually(self, main_tracker, main_proceso_id, tiempo_inicio, parametros_proceso):
        """
        NUEVA FUNCIÓN: Procesa cada hoja de Excel por separado creando tabla individual
        Cada hoja genera su propio registro en ProcesoLog y ResultadosProcesados
        
        Returns:
            Tuple[bool, Dict]: (éxito_general, información_consolidada)
        """
        from .data_transfer_service import data_transfer_service
        from .logs.process_tracker import ProcessTracker
        import pandas as pd
        import json
        
        try:
            if not self.source.file_path:
                raise Exception('No hay archivo Excel configurado')
            
            # Obtener hojas seleccionadas
            selected_sheets = self.selected_sheets if isinstance(self.selected_sheets, list) else (json.loads(self.selected_sheets) if self.selected_sheets else [])
            if not selected_sheets:
                raise Exception('No hay hojas seleccionadas en el Excel')
            
            # Variables para consolidar resultados
            hojas_procesadas = []
            hojas_con_error = []
            total_registros_procesados = 0
            
            main_tracker.actualizar_estado('PROCESANDO_HOJAS', f'Procesando {len(selected_sheets)} hojas de Excel por separado')
            
            # PROCESAR CADA HOJA POR SEPARADO
            for sheet_name in selected_sheets:
                hoja_inicio = timezone.now()
                print(f"🚀 Procesando hoja Excel: '{sheet_name}'")
                
                try:
                    # 1. Crear tracker individual para esta hoja
                    nombre_proceso_hoja = f"{self.name} - Hoja: {sheet_name}"
                    tracker_hoja = ProcessTracker(nombre_proceso_hoja)
                    
                    # Parámetros específicos de la hoja
                    parametros_hoja = parametros_proceso.copy()
                    parametros_hoja.update({
                        'sheet_name': sheet_name,
                        'parent_process_id': main_proceso_id,
                        'is_excel_sheet': True
                    })
                    
                    # Iniciar proceso individual para esta hoja
                    proceso_id_hoja = tracker_hoja.iniciar(parametros_hoja)
                    
                    # 2. Extraer datos específicos de esta hoja
                    df = pd.read_excel(self.source.file_path, sheet_name=sheet_name)
                    
                    # Aplicar limpieza de datos (nombres de columnas y valores NaN)
                    df = self._clean_excel_dataframe(df)
                    
                    # Filtrar columnas si están especificadas para esta hoja
                    if self.selected_columns:
                        selected_cols = (self.selected_columns.get(sheet_name, []) if isinstance(self.selected_columns, dict) 
                                       else json.loads(self.selected_columns).get(sheet_name, [])) if self.selected_columns else []
                        if selected_cols:
                            df = df[selected_cols]
                    
                    # Convertir a diccionarios para transferencia
                    datos_hoja = df.to_dict('records')
                    registros_hoja = len(datos_hoja)
                    
                    tracker_hoja.actualizar_estado('EXTRAYENDO_DATOS', f'Extraídos {registros_hoja} registros de la hoja {sheet_name}')
                    
                    # 3. Preparar resumen específico de esta hoja
                    hoja_fin = timezone.now()
                    duracion_hoja = (hoja_fin - hoja_inicio).total_seconds()
                    
                    resumen_hoja = {
                        'proceso_ejecutado': nombre_proceso_hoja,
                        'hoja_excel': sheet_name,
                        'archivo_origen': self.source.name,
                        'timestamp_ejecucion': hoja_inicio.isoformat(),
                        'estadisticas': {
                            'total_registros': registros_hoja,
                            'total_columnas': len(df.columns),
                            'columnas_procesadas': list(df.columns),
                            'duracion_extraccion_segundos': round(duracion_hoja, 2),
                            'tipo_fuente': 'excel'
                        },
                        'configuracion': {
                            'hoja_seleccionada': sheet_name,
                            'columnas_seleccionadas': (self.selected_columns.get(sheet_name, []) if isinstance(self.selected_columns, dict) 
                                                     else json.loads(self.selected_columns).get(sheet_name, [])) if self.selected_columns else list(df.columns),
                            'base_datos_destino': self.target_db_name or 'DestinoAutomatizacion'
                        }
                    }
                    
                    # Metadatos específicos de la hoja
                    metadata_hoja = {
                        'migration_process_id': self.id,
                        'process_name': self.name,
                        'sheet_name': sheet_name,
                        'parent_process_id': main_proceso_id,
                        'source_type': 'excel',
                        'source_id': self.source.id,
                        'execution_timestamp': hoja_inicio.isoformat(),
                        'file_name': self.source.name,
                        'columns_count': len(df.columns),
                        'selected_columns': (self.selected_columns.get(sheet_name, []) if isinstance(self.selected_columns, dict) else json.loads(self.selected_columns).get(sheet_name, [])) if self.selected_columns else list(df.columns),
                        'target_db_name': self.target_db_name,
                        'extraction_duration_seconds': duracion_hoja
                    }
                    
                    # 4. Transferir datos de esta hoja a su tabla individual
                    tracker_hoja.actualizar_estado('TRANSFIRIENDO', f'Creando tabla individual para hoja {sheet_name}')
                    
                    # Normalizar nombre de hoja para usar como nombre de tabla
                    table_friendly_name = self._normalize_table_name(sheet_name)
                    
                    success_hoja, result_info_hoja = data_transfer_service.transfer_to_dynamic_table(
                        process_name=table_friendly_name,  # ✅ NOMBRE LIMPIO PARA LA TABLA
                        proceso_id=proceso_id_hoja,
                        datos_procesados=resumen_hoja,
                        usuario_responsable='sistema_automatizado',
                        metadata=metadata_hoja,
                        recreate_table=True,
                        estado_proceso='COMPLETADO',
                        tipo_operacion=f'MIGRACION_EXCEL_{table_friendly_name.upper().replace(" ", "_")}',
                        registros_afectados=registros_hoja
                    )
                    
                    # DEBUG: Logging adicional para detectar el problema
                    # Debug logging removido para producción
                    # if not success_hoja:
                    #     print(f"DEBUG Error info: {result_info_hoja}")
                    
                    if success_hoja:
                        # ✅ Hoja procesada exitosamente
                        table_name = result_info_hoja.get('table_name', f'Proceso_{sheet_name}')
                        resultado_id = result_info_hoja.get('resultado_id', 'N/A')
                        
                        # Finalizar proceso exitosamente para esta hoja
                        detalles_exito_hoja = f"Hoja Excel '{sheet_name}' procesada exitosamente. Tabla: {table_name}, ResultadoID: {resultado_id}, Registros: {registros_hoja}"
                        tracker_hoja.finalizar_exito(detalles_exito_hoja)
                        
                        # Agregar a resultados exitosos
                        hojas_procesadas.append({
                            'sheet_name': sheet_name,
                            'table_name': table_name,
                            'registros': registros_hoja,
                            'resultado_id': resultado_id,
                            'proceso_id': proceso_id_hoja,
                            'duracion': duracion_hoja
                        })
                        
                        total_registros_procesados += registros_hoja
                        
                        print(f"✅ Hoja '{sheet_name}' procesada exitosamente:")
                        print(f"   📋 Tabla creada: '{table_name}'")
                        print(f"   📊 Registros: {registros_hoja}")
                        print(f"   🆔 ResultadoID: {resultado_id}")
                        print(f"   🔗 ProcesoID: {proceso_id_hoja}")
                        
                    else:
                        # ❌ Error procesando esta hoja
                        error_msg_hoja = result_info_hoja.get('error', 'Error desconocido procesando hoja')
                        error_completo_hoja = f"Error procesando hoja '{sheet_name}': {error_msg_hoja}"
                        
                        # Registrar error para esta hoja
                        tracker_hoja.finalizar_error(Exception(error_completo_hoja))
                        
                        hojas_con_error.append({
                            'sheet_name': sheet_name,
                            'error': error_msg_hoja,
                            'proceso_id': proceso_id_hoja
                        })
                        
                        print(f"❌ Error procesando hoja '{sheet_name}': {error_msg_hoja}")
                
                except Exception as e_hoja:
                    # Error específico procesando esta hoja
                    error_hoja = f"Error procesando hoja '{sheet_name}': {str(e_hoja)}"
                    
                    # Si tenemos tracker para esta hoja, registrar error
                    if 'tracker_hoja' in locals():
                        tracker_hoja.finalizar_error(e_hoja)
                    
                    hojas_con_error.append({
                        'sheet_name': sheet_name,
                        'error': str(e_hoja),
                        'proceso_id': locals().get('proceso_id_hoja', 'N/A')
                    })
                    
                    print(f"❌ Error procesando hoja '{sheet_name}': {str(e_hoja)}")
            
            # CONSOLIDAR RESULTADOS FINALES
            tiempo_fin_total = timezone.now()
            duracion_total = (tiempo_fin_total - tiempo_inicio).total_seconds()
            
            hojas_exitosas = len(hojas_procesadas)
            hojas_fallidas = len(hojas_con_error)
            
            # Determinar éxito general
            success_general = hojas_exitosas > 0  # Al menos una hoja debe procesarse exitosamente
            
            # Preparar información consolidada
            result_info_consolidado = {
                'success': success_general,
                'hojas_procesadas': hojas_exitosas,
                'hojas_con_error': hojas_fallidas,
                'total_hojas': len(selected_sheets),
                'total_registros': total_registros_procesados,
                'duracion_total': duracion_total,
                'detalles_hojas_exitosas': hojas_procesadas,
                'detalles_hojas_error': hojas_con_error,
                'table_name': f'Múltiples tablas creadas ({hojas_exitosas} exitosas)',
                'resultado_id': f'{hojas_exitosas} tablas creadas',
                'process_type': 'excel_multi_sheet'
            }
            
            # Actualizar estado del tracker principal
            if success_general:
                estado_final = f"Excel procesado: {hojas_exitosas}/{len(selected_sheets)} hojas exitosas, {total_registros_procesados} registros totales"
                main_tracker.actualizar_estado('COMPLETADO', estado_final)
            else:
                estado_final = f"Error procesando Excel: {hojas_fallidas}/{len(selected_sheets)} hojas fallaron"
                main_tracker.actualizar_estado('ERROR', estado_final)
            
            print(f"\n📊 RESUMEN PROCESAMIENTO EXCEL:")
            print(f"   📋 Total hojas: {len(selected_sheets)}")
            print(f"   ✅ Hojas exitosas: {hojas_exitosas}")
            print(f"   ❌ Hojas con error: {hojas_fallidas}")
            print(f"   📊 Total registros: {total_registros_procesados}")
            print(f"   ⏱️ Duración total: {duracion_total:.2f}s")
            
            return success_general, result_info_consolidado
            
        except Exception as e:
            # Error general procesando el archivo Excel
            error_msg = f'Error general procesando Excel: {str(e)}'
            main_tracker.actualizar_estado('ERROR', error_msg)
            
            return False, {
                'success': False,
                'error': error_msg,
                'hojas_procesadas': 0,
                'hojas_con_error': len(selected_sheets) if 'selected_sheets' in locals() else 0,
                'process_type': 'excel_multi_sheet_error'
            }
    
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
    
    def _normalize_table_name(self, sheet_name):
        """
        Normaliza el nombre de una hoja de Excel para usar como nombre de tabla
        
        Args:
            sheet_name (str): Nombre original de la hoja
            
        Returns:
            str: Nombre normalizado apto para usar como tabla
        """
        import re
        
        # Remover/reemplazar caracteres especiales
        normalized = sheet_name
        
        # Reemplazos específicos para caracteres problemáticos
        normalized = normalized.replace('Ñ', 'N').replace('ñ', 'n')
        normalized = normalized.replace('Á', 'A').replace('á', 'a')
        normalized = normalized.replace('É', 'E').replace('é', 'e')
        normalized = normalized.replace('Í', 'I').replace('í', 'i')
        normalized = normalized.replace('Ó', 'O').replace('ó', 'o')
        normalized = normalized.replace('Ú', 'U').replace('ú', 'u')
        normalized = normalized.replace('Ü', 'U').replace('ü', 'u')
        
        # Reemplazar espacios y caracteres especiales con guiones bajos
        normalized = re.sub(r'[^\w\s-]', '_', normalized)
        normalized = re.sub(r'[\s-]+', '_', normalized)
        
        # Remover guiones bajos al inicio y final
        normalized = normalized.strip('_')
        
        # Asegurar que no esté vacío y que sea válido
        if not normalized or normalized.isdigit():
            normalized = f'Hoja_{normalized or "1"}'
        
        # Limitar longitud
        if len(normalized) > 50:
            normalized = normalized[:50].rstrip('_')
            
        return normalized
    
    def _clean_excel_dataframe(self, df):
        """
        Limpia el DataFrame de Excel: renombra columnas Unnamed y reemplaza valores NaN
        """
        import pandas as pd
        import numpy as np
        
        # Limpiar nombres de columnas
        new_columns = []
        unnamed_counter = 1
        
        for col in df.columns:
            col_str = str(col)
            if col_str.startswith('Unnamed'):
                # Renombrar columnas Unnamed con un nombre más descriptivo
                new_name = f'Columna_{unnamed_counter}'
                unnamed_counter += 1
            elif pd.isna(col) or col_str.lower() in ['nan', 'null', '']:
                # Manejar columnas con nombres nulos o vacíos
                new_name = f'Columna_{unnamed_counter}'
                unnamed_counter += 1
            else:
                new_name = col_str
            
            new_columns.append(new_name)
        
        # Aplicar nuevos nombres de columnas
        df.columns = new_columns
        
        # Reemplazar valores NaN, None, y variantes de 'nan'
        df = df.fillna('')  # Reemplazar NaN con cadena vacía
        
        # Reemplazar valores de texto que son 'nan', 'null', etc.
        for col in df.columns:
            if df[col].dtype == 'object':  # Columnas de texto
                df[col] = df[col].astype(str)
                df[col] = df[col].replace({
                    'nan': '',
                    'NaN': '',
                    'null': '',
                    'NULL': '',
                    'None': '',
                    '<NA>': ''
                })
        
        return df

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