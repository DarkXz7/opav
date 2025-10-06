import os
import json
import pandas as pd
import tempfile
from datetime import datetime

from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.http import JsonResponse, HttpResponse
from django.conf import settings
from django.contrib import messages
from django.core.files.storage import FileSystemStorage
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.db import models

# Importar decoradores de logging
from .decorators import log_operation
from .decorators_optimized import log_operation_unified
from .frontend_logging import auto_log_frontend_process

from .models import DataSourceType, DataSource, DatabaseConnection, MigrationProcess, MigrationLog
from .utils import ExcelProcessor, CSVProcessor, SQLServerConnector, TargetDBManager

# Vistas principales

def index(request):
    """Vista principal de la aplicación"""
    # Obtener procesos guardados para mostrarlos en la página principal
    recent_processes = MigrationProcess.objects.all().order_by('-created_at')[:5]
    saved_connections = DatabaseConnection.objects.all().order_by('-created_at')[:5]
    
    context = {
        'recent_processes': recent_processes,
        'saved_connections': saved_connections
    }
    return render(request, 'automatizacion/index.html', context)

def new_process(request):
    """Inicia un nuevo proceso de migración"""
    context = {
        'source_types': [
            {'id': 'excel', 'name': 'Excel (.xlsx)'},
            {'id': 'csv', 'name': 'CSV'},
            {'id': 'sql', 'name': 'SQL Server'}
        ],
        'connections': DatabaseConnection.objects.all()
    }
    return render(request, 'automatizacion/new_process.html', context)

def list_processes(request):
    """Lista todos los procesos de migración guardados"""
    processes = MigrationProcess.objects.all().order_by('-created_at')
    return render(request, 'automatizacion/list_processes.html', {'processes': processes})

def view_process(request, process_id):
    """Muestra los detalles de un proceso guardado"""
    process = get_object_or_404(MigrationProcess, pk=process_id)
    logs = process.logs.all().order_by('-timestamp')[:10]
    
    # Obtener detalles según tipo de fuente
    context = {
        'process': process,
        'logs': logs
    }
    
    if process.source.source_type == 'excel' or process.source.source_type == 'csv':
        context['file_path'] = process.source.file_path
    elif process.source.source_type == 'sql':
        context['connection'] = process.source.connection
        
    return render(request, 'automatizacion/view_process.html', context)

def run_process(request, process_id):
    """
    Ejecuta un proceso guardado 
    ✅ CORREGIDO: Elimina logging duplicado y usa solo el log del modelo MigrationProcess.run()
    """
    process = get_object_or_404(MigrationProcess, pk=process_id)
    
    try:
        print(f"🚀 Iniciando ejecución del proceso: {process.name} (ID: {process.id})")
        
        # ✅ CORRECCIÓN: Usar SOLO process.run() que ya maneja el logging correctamente
        # Esto evita logs duplicados y asegura que MigrationProcessID sea correcto
        process.run()
        
        messages.success(request, f'El proceso "{process.name}" se ha ejecutado correctamente y los datos se han guardado en DestinoAutomatizacion.')
        
    except Exception as e:
        print(f"❌ Error ejecutando proceso {process.name}: {str(e)}")
        
        # ✅ CORRECCIÓN: El manejo de errores ya está en process.run() 
        # No necesitamos manejo adicional aquí
        messages.error(request, f'Error al ejecutar el proceso: {str(e)}')
    
    return redirect('automatizacion:view_process', process_id=process.id)

def delete_process(request, process_id):
    """Elimina un proceso guardado con confirmación"""
    process = get_object_or_404(MigrationProcess, pk=process_id)
    
    if request.method == 'POST':
        try:
            process_name = process.name
            process_id_deleted = process.id
            
            # Eliminar el proceso
            process.delete()
            
            messages.success(
                request, 
                f'El proceso "{process_name}" (ID: {process_id_deleted}) ha sido eliminado exitosamente.'
            )
            return redirect('automatizacion:list_processes')
            
        except Exception as e:
            messages.error(
                request, 
                f'Error al eliminar el proceso "{process.name}": {str(e)}'
            )
            return render(request, 'automatizacion/confirm_delete.html', {'process': process})
    
    # GET request - mostrar página de confirmación
    return render(request, 'automatizacion/confirm_delete.html', {'process': process})

# Vistas para Excel/CSV

def upload_excel(request):
    """Maneja la carga de archivos Excel/CSV - SIN LOGGING INDIVIDUAL"""
    
    # NO crear logger aquí - será creado solo en save_process al final del flujo
    
    if request.method == 'POST' and request.FILES.get('file'):
        uploaded_file = request.FILES['file']
        file_type = request.POST.get('file_type', 'excel')
        
        # NO crear logging aquí - será manejado en save_process
        
        try:
            # Guardar el archivo
            fs = FileSystemStorage(location=settings.TEMP_DIR)
            filename = fs.save(uploaded_file.name, uploaded_file)
            file_path = fs.path(filename)
            
            # Crear registro de fuente de datos
            source = DataSource.objects.create(
                name=uploaded_file.name,
                source_type=file_type,
                file_path=file_path
            )
            
            # NO registrar aquí - será registrado en save_process al final
            
            if file_type == 'excel':
                return redirect('automatizacion:list_excel_sheets', source_id=source.id)
            else:  # CSV
                return redirect('automatizacion:list_excel_columns', source_id=source.id, sheet_name='csv_data')
        
        except Exception as e:
            # NO registrar error aquí - solo mostrar al usuario
            
            # Mostrar mensaje de error al usuario
            messages.error(request, f"Error al procesar el archivo: {str(e)}")
            return render(request, 'automatizacion/upload_excel.html')
            
    return render(request, 'automatizacion/upload_excel.html')

@log_operation_unified("Exploración de hojas Excel")
def list_excel_sheets(request, source_id):
    """Lista las hojas de un archivo Excel"""
    source = get_object_or_404(DataSource, pk=source_id)
    
    if source.source_type != 'excel':
        messages.error(request, 'La fuente de datos no es un archivo Excel')
        return redirect('automatizacion:index')
        
    processor = ExcelProcessor(source.file_path)
    if not processor.load_file():
        messages.error(request, 'No se pudo cargar el archivo Excel')
        return redirect('automatizacion:upload_excel')
        
    sheets = processor.get_sheet_names()
    
    # Obtener vista previa de cada hoja
    sheet_previews = {}
    for sheet in sheets:
        preview = processor.get_sheet_preview(sheet)
        if preview:
            sheet_previews[sheet] = {
                'total_rows': preview['total_rows'],
                'columns': len(preview['columns'])
            }
    
    context = {
        'source': source,
        'sheets': sheets,
        'previews': sheet_previews
    }
    
    return render(request, 'automatizacion/list_excel_sheets.html', context)

def list_excel_columns(request, source_id, sheet_name):
    """Lista las columnas de una hoja de Excel o archivo CSV"""
    source = get_object_or_404(DataSource, pk=source_id)
    
    if source.source_type == 'excel':
        processor = ExcelProcessor(source.file_path)
        if not processor.load_file():
            messages.error(request, 'No se pudo cargar el archivo Excel')
            return redirect('automatizacion:upload_excel')
            
        columns = processor.get_sheet_columns(sheet_name)
        preview = processor.get_sheet_preview(sheet_name)
    else:  # CSV
        processor = CSVProcessor(source.file_path)
        columns = processor.get_columns()
        preview = processor.get_preview()
        sheet_name = 'csv_data'  # Nombre genérico para CSV
    
    context = {
        'source': source,
        'sheet_name': sheet_name,
        'columns': columns,
        'preview': preview
    }
    
    return render(request, 'automatizacion/list_columns.html', context)

# Vistas para SQL Server

@log_operation("Conexión a SQL Server")
def connect_sql(request):
    """Maneja la conexión a un servidor SQL Server"""
    if request.method == 'POST':
        # Obtener datos de conexión
        name = request.POST.get('name')
        server = request.POST.get('server')
        username = request.POST.get('username')
        password = request.POST.get('password')
        port = request.POST.get('port', '1433')
        
        # Validar datos
        if not all([name, server, username, password]):
            messages.error(request, 'Todos los campos son obligatorios')
            return render(request, 'automatizacion/connect_sql.html', {
                'form_data': {
                    'name': name or '',
                    'server': server or '',
                    'username': username or '',
                    'port': port,
                    'database': request.POST.get('database', '')
                }
            })
        
        # Probar conexión al servidor (sin especificar base de datos)
        connector = SQLServerConnector(server, username, password, port)
        if not connector.test_connection():
            messages.error(request, 'No se pudo conectar al servidor. Verifique los datos de conexión.')
            return render(request, 'automatizacion/connect_sql.html', {
                'form_data': {
                    'name': name,
                    'server': server,
                    'username': username,
                    'port': port,
                    'database': request.POST.get('database', '')
                }
            })
        
        # Obtener la lista de bases de datos disponibles
        databases = connector.get_databases()
        
        # Verificar si ya existe una conexión con el mismo nombre
        existing_connection = DatabaseConnection.objects.filter(name=name).first()
        
        if existing_connection:
            # No permitir crear conexión con nombre duplicado
            messages.error(request, f'Ya existe una conexión con el nombre "{name}". Por favor, elija un nombre diferente.')
            return render(request, 'automatizacion/connect_sql.html', {
                'form_data': {
                    'name': name,
                    'server': server,
                    'username': username,
                    'port': port,
                    'database': request.POST.get('database', '')
                }
            })
        
        # Crear nueva conexión
        connection = DatabaseConnection.objects.create(
            name=name,
            server=server,
            username=username,
            password=password,
            port=port,
            last_used=timezone.now(),
            available_databases=databases
        )
        messages.success(request, 'Nueva conexión creada correctamente')
        
        # Redirigir a la página de selección de base de datos
        return redirect('automatizacion:list_sql_databases', connection_id=connection.id)
        
    return render(request, 'automatizacion/connect_sql.html')

def list_connections(request):
    """Lista todas las conexiones guardadas (solo una por nombre único)"""
    # Obtener solo una conexión por cada nombre único, priorizando la más reciente
    connections = DatabaseConnection.objects.values('name').annotate(
        latest_id=models.Max('id'),
        latest_created=models.Max('created_at')
    ).order_by('-latest_created')
    
    # Obtener las conexiones completas basadas en los IDs únicos
    connection_ids = [conn['latest_id'] for conn in connections]
    unique_connections = DatabaseConnection.objects.filter(id__in=connection_ids).order_by('-created_at')
    
    return render(request, 'automatizacion/list_connections.html', {'connections': unique_connections})

@log_operation("Vista de conexión SQL")
def view_connection(request, connection_id):
    """Muestra detalles de una conexión guardada"""
    connection = get_object_or_404(DatabaseConnection, pk=connection_id)
    return render(request, 'automatizacion/view_connection.html', {'connection': connection})

@log_operation("Listado de bases de datos SQL")
def list_sql_databases(request, connection_id):
    """Lista todas las bases de datos disponibles en el servidor SQL"""
    connection = get_object_or_404(DatabaseConnection, pk=connection_id)
    
    # Actualizar fecha de último uso
    connection.last_used = timezone.now()
    connection.save()
    
    # Si ya tenemos bases de datos almacenadas, usarlas
    if connection.available_databases:
        databases = connection.available_databases
    else:
        # Si no, obtenerlas del servidor
        connector = SQLServerConnector(
            connection.server,
            connection.username,
            connection.password,
            connection.port
        )
        
        databases = connector.get_databases()
        
        # Guardar la lista de bases de datos en la conexión
        connection.available_databases = databases
        connection.save()
    
    context = {
        'connection': connection,
        'databases': databases
    }
    
    return render(request, 'automatizacion/list_sql_databases.html', context)

def select_database(request, connection_id):
    """Selecciona la base de datos especificada por el usuario"""
    connection = get_object_or_404(DatabaseConnection, pk=connection_id)
    
    if request.method == 'POST':
        # Obtener la base de datos seleccionada por el usuario
        selected_database = request.POST.get('selected_database')
        
        if not selected_database:
            messages.error(request, 'Debe seleccionar una base de datos')
            return redirect('automatizacion:list_sql_databases', connection_id=connection_id)
        
        # Probar la conexión a la base de datos seleccionada
        connector = SQLServerConnector(
            connection.server,
            connection.username,
            connection.password,
            connection.port
        )
        
        if not connector.select_database(selected_database):
            messages.error(request, f'No se pudo conectar a la base de datos {selected_database}')
            return redirect('automatizacion:list_sql_databases', connection_id=connection_id)
        
        # Actualizar la conexión con la base de datos seleccionada
        connection.selected_database = selected_database
        connection.save()
        
        # Crear o actualizar la fuente de datos
        source, created = DataSource.objects.get_or_create(
            source_type='sql',
            connection=connection,
            defaults={'name': f"SQL - {connection.name} - {selected_database}"}
        )
        
        if not created:
            source.name = f"SQL - {connection.name} - {selected_database}"
            source.save()
        
        messages.success(request, f'Base de datos {selected_database} seleccionada correctamente')
        return redirect('automatizacion:list_sql_tables', connection_id=connection_id)
    
    return redirect('automatizacion:list_sql_databases', connection_id=connection_id)

@log_operation("Listado de tablas SQL")
def list_sql_tables(request, connection_id):
    """Lista las tablas de una base de datos SQL Server"""
    connection = get_object_or_404(DatabaseConnection, pk=connection_id)
    
    # Verificar que se haya seleccionado una base de datos
    if not connection.selected_database:
        messages.warning(request, 'Debe seleccionar una base de datos primero')
        return redirect('automatizacion:list_sql_databases', connection_id=connection_id)
    
    # Actualizar fecha de último uso
    connection.last_used = timezone.now()
    connection.save()
    
    connector = SQLServerConnector(
        connection.server,
        connection.username,
        connection.password,
        connection.port
    )
    
    # Conectar a la base de datos seleccionada
    if not connector.select_database(connection.selected_database):
        messages.error(request, f'No se pudo conectar a la base de datos {connection.selected_database}')
        return redirect('automatizacion:list_sql_databases', connection_id=connection_id)
    
    tables = connector.get_tables()
    
    # Verificar que cada tabla tenga un full_name válido
    for table in tables:
        if 'full_name' not in table or not table['full_name']:
            # Si no hay full_name, construirlo usando schema y name
            table['full_name'] = f"{table.get('schema', 'dbo')}.{table.get('name', '')}"
    
    # Buscar o crear fuente de datos para esta conexión
    source, created = DataSource.objects.get_or_create(
        source_type='sql',
        connection=connection,
        defaults={'name': f"SQL - {connection.name} - {connection.selected_database}"}
    )
    
    context = {
        'connection': connection,
        'database': connection.selected_database,
        'tables': tables,
        'source': source
    }
    
    return render(request, 'automatizacion/list_sql_tables.html', context)

from .decorators import log_operation

def list_sql_columns(request, connection_id, table_name):
    """Lista las columnas de una tabla SQL - SIN LOGGING INDIVIDUAL"""
    
    # NO crear logging aquí - será creado solo en save_process al final del flujo
    
    connection = get_object_or_404(DatabaseConnection, pk=connection_id)
    
    # Verificar que se haya seleccionado una base de datos
    if not connection.selected_database:
        # NO registrar aquí - será manejado en save_process
        messages.warning(request, 'Debe seleccionar una base de datos primero')
        return redirect('automatizacion:list_sql_databases', connection_id=connection_id)
    
    try:
        # Separar esquema y nombre de tabla
        parts = table_name.split('.')
        if len(parts) == 2:
            schema, table = parts
        else:
            schema = 'dbo'  # Esquema por defecto
            table = table_name
            
        # Verificar que tengamos valores válidos
        if not schema or not table:
            # NO registrar aquí - será manejado en save_process
            messages.error(request, 'Nombre de tabla inválido. Formato esperado: [esquema].[tabla]')
            return redirect('automatizacion:list_sql_tables', connection_id=connection_id)
        
        connector = SQLServerConnector(
            connection.server,
            connection.username,
            connection.password,
            connection.port
        )
        
        # Conectar a la base de datos seleccionada
        if not connector.select_database(connection.selected_database):
            # NO registrar aquí - será manejado en save_process
            messages.error(request, f'No se pudo conectar a la base de datos {connection.selected_database}')
            return redirect('automatizacion:list_sql_databases', connection_id=connection_id)
    except Exception as e:
        # NO registrar aquí - será manejado en save_process
        messages.error(request, f'Error al procesar el nombre de la tabla: {str(e)}')
        return redirect('automatizacion:list_sql_tables', connection_id=connection_id)
    
    columns = connector.get_table_columns(schema, table)
    preview = connector.get_table_preview(schema, table)
    
    # Buscar fuente de datos para esta conexión
    source, created = DataSource.objects.get_or_create(
        source_type='sql',
        connection=connection,
        defaults={'name': f"SQL - {connection.name}"}
    )
    
    context = {
        'connection': connection,
        'schema': schema,
        'table_name': table,
        'full_table_name': f"{schema}.{table}",
        'columns': columns,
        'preview': preview,
        'source': source
    }
    
    # NO registrar aquí - será registrado en save_process al final del flujo
    
    return render(request, 'automatizacion/list_sql_columns.html', context)

# Vistas para API AJAX

@csrf_exempt
def save_process(request):
    """Guarda un proceso de migración (endpoint AJAX)"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Solo se permiten solicitudes POST'}, status=405)
    
    # Iniciar tracking del proceso
    from .web_logger_optimized import registrar_proceso_web, finalizar_proceso_web
    
    try:
        data = json.loads(request.body)
        
        # Obtener el nombre del proceso del frontend
        process_name = data.get('name', 'Proceso sin nombre')
        
        # LOG DETALLADO PARA DEPURACIÓN
        print(f"DEBUG: save_process llamado por usuario {request.user}")
        print(f"DEBUG: Datos recibidos: {data}")
        print(f"DEBUG: Nombre del proceso: '{process_name}'")
        
        # Iniciar logger optimizado
        print(f"DEBUG: Iniciando logger para proceso '{process_name}'")
        tracker, proceso_id = registrar_proceso_web(
            nombre_proceso=f"Guardado de proceso: {process_name}",
            usuario=request.user,
            datos_adicionales={
                'process_name': process_name,
                'source_id': data.get('source_id'),
                'selected_tables': data.get('selected_tables'),
                'selected_database': data.get('selected_database'),
                'action': 'save_process',
                'user_agent': request.META.get('HTTP_USER_AGENT', 'Unknown'),
                'remote_addr': request.META.get('REMOTE_ADDR', 'Unknown')
            }
        )
        print(f"DEBUG: Logger iniciado - tracker={tracker}, proceso_id={proceso_id}")
        
        # Validar datos requeridos
        if not data.get('name') or not data.get('source_id'):
            return JsonResponse({'error': 'Nombre y fuente de datos son obligatorios'}, status=400)
        
        # Obtener fuente de datos
        source = get_object_or_404(DataSource, pk=data.get('source_id'))
        
        # Crear o actualizar proceso
        process_id = data.get('process_id')
        process_name = data.get('name')
        
        print(f"DEBUG: process_id recibido: {process_id}, process_name: {process_name}")
        
        if process_id:
            # Verificar si el proceso existe
            try:
                process = MigrationProcess.objects.get(pk=process_id)
                print(f"DEBUG: Proceso encontrado para actualización: ID {process.id}, nombre actual: '{process.name}'")
                
                # Verificar si el nuevo nombre ya existe en otro proceso
                existing_process = MigrationProcess.objects.filter(name=process_name).exclude(id=process.id).first()
                if existing_process:
                    return JsonResponse({
                        'error': f'Ya existe un proceso con el nombre "{process_name}". Por favor, elija un nombre diferente.'
                    }, status=400)
                
                process.name = process_name
                process.description = data.get('description', '')
                print(f"DEBUG: Actualizando proceso existente con nuevo nombre: '{process_name}'")
                
            except MigrationProcess.DoesNotExist:
                print(f"DEBUG: Proceso con ID {process_id} no encontrado, creando uno nuevo")
                # Si el proceso no existe, crear uno nuevo
                existing_process = MigrationProcess.objects.filter(name=process_name).first()
                if existing_process:
                    return JsonResponse({
                        'error': f'Ya existe un proceso con el nombre "{process_name}". Por favor, elija un nombre diferente.'
                    }, status=400)
                
                # Crear nuevo proceso
                process = MigrationProcess(
                    name=process_name,
                    description=data.get('description', ''),
                    source=source
                )
        else:
            print(f"DEBUG: Creando nuevo proceso con nombre: '{process_name}'")
            # Verificar si ya existe un proceso con el mismo nombre
            existing_process = MigrationProcess.objects.filter(name=process_name).first()
            if existing_process:
                return JsonResponse({
                    'error': f'Ya existe un proceso con el nombre "{process_name}". Por favor, elija un nombre diferente.'
                }, status=400)
            
            # Crear nuevo proceso
            process = MigrationProcess(
                name=process_name,
                description=data.get('description', ''),
                source=source
            )
        
        # Guardar detalles según tipo de fuente
        if source.source_type in ['excel', 'csv']:
            process.selected_sheets = data.get('selected_sheets')
        elif source.source_type == 'sql':
            process.selected_tables = data.get('selected_tables')
        
        process.selected_columns = data.get('selected_columns')
        process.target_db_name = data.get('target_db', 'default')
        
        process.save()
        
        # Finalizar logger con éxito
        print(f"DEBUG: Finalizando logger con éxito para proceso Django ID {process.id}")
        print(f"DEBUG: Proceso guardado: {process.name} (Source: {process.source.name})")
        finalizar_proceso_web(
            tracker,
            usuario=request.user,
            exito=True,
            detalles=f"Proceso '{process_name}' guardado exitosamente. Django ID: {process.id}, Proceso UUID: {proceso_id}"
        )
        print("DEBUG: Logger finalizado exitosamente")
        
        return JsonResponse({
            'success': True,
            'process_id': process.id,
            'proceso_id': proceso_id,  # UUID del sistema de logging
            'message': 'Proceso guardado correctamente'
        })
    
    except Exception as e:
        # LOG DETALLADO DEL ERROR
        print(f"ERROR en save_process: {str(e)}")
        print(f"ERROR tipo: {type(e).__name__}")
        import traceback
        print(f"ERROR traceback: {traceback.format_exc()}")
        
        # Finalizar logger con error
        if 'tracker' in locals():
            print("DEBUG: Finalizando tracker con error...")
            finalizar_proceso_web(
                tracker,
                usuario=request.user,
                exito=False,
                error=e
            )
            print("DEBUG: Tracker finalizado con error")
        
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
def delete_connection(request, connection_id):
    """Elimina una conexión guardada (endpoint AJAX)"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Solo se permiten solicitudes POST'}, status=405)
    
    try:
        connection = get_object_or_404(DatabaseConnection, pk=connection_id)
        
        # Eliminar también las fuentes de datos asociadas
        DataSource.objects.filter(connection=connection).delete()
        
        connection_name = connection.name
        connection.delete()
        
        return JsonResponse({
            'success': True,
            'message': f'La conexión "{connection_name}" ha sido eliminada'
        })
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def edit_process(request, process_id):
    """Permite editar un proceso guardado"""
    process = get_object_or_404(MigrationProcess, pk=process_id)
    
    if request.method == 'POST':
        # Actualizar los campos del proceso
        process.name = request.POST.get('name', process.name)
        process.description = request.POST.get('description', process.description)
        
        # Actualizar campos específicos según el tipo de fuente
        if process.source.source_type in ['excel', 'csv']:
            # Para Excel/CSV, actualizar hojas/columnas seleccionadas
            if 'selected_sheets' in request.POST:
                import json
                try:
                    process.selected_sheets = json.loads(request.POST.get('selected_sheets'))
                except:
                    pass
            
            if 'selected_columns' in request.POST:
                import json
                try:
                    process.selected_columns = json.loads(request.POST.get('selected_columns'))
                except:
                    pass
                    
        elif process.source.source_type == 'sql':
            # Para SQL, actualizar base de datos, tablas y columnas
            process.selected_database = request.POST.get('selected_database', process.selected_database)
            
            if 'selected_tables' in request.POST:
                import json
                try:
                    process.selected_tables = json.loads(request.POST.get('selected_tables'))
                except:
                    pass
            
            if 'selected_columns' in request.POST:
                import json
                try:
                    process.selected_columns = json.loads(request.POST.get('selected_columns'))
                except:
                    pass
        
        # Guardar cambios
        process.save()
        
        # Crear log de modificación
        from .models import MigrationLog
        MigrationLog.log(
            process=process,
            stage='validation',
            message=f'Proceso modificado por usuario',
            level='info',
            user=request.user.username if request.user.is_authenticated else 'anónimo'
        )
        
        messages.success(request, f'El proceso "{process.name}" ha sido actualizado correctamente.')
        return redirect('automatizacion:view_process', process_id=process.id)
    
    # GET - Mostrar formulario de edición
    context = {
        'process': process,
        'source': process.source
    }
    
    # Obtener información específica según tipo de fuente
    if process.source.source_type == 'excel':
        # Para Excel, obtener información de hojas disponibles
        context['file_path'] = process.source.file_path
        try:
            from .utils import ExcelProcessor
            processor = ExcelProcessor(process.source.file_path)
            context['available_sheets'] = processor.get_sheet_names()
        except Exception as e:
            context['available_sheets'] = []
            messages.warning(request, f'No se pudieron cargar las hojas del archivo: {str(e)}')
            
    elif process.source.source_type == 'csv':
        # Para CSV
        context['file_path'] = process.source.file_path
        
    elif process.source.source_type == 'sql':
        # Para SQL, obtener información de conexión
        context['connection'] = process.source.connection
        try:
            from .utils import DatabaseInspector
            inspector = DatabaseInspector(process.source.connection)
            context['available_databases'] = inspector.get_databases()
            
            if process.selected_database:
                context['available_tables'] = inspector.get_tables(process.selected_database)
        except Exception as e:
            context['available_databases'] = []
            context['available_tables'] = []
            messages.warning(request, f'No se pudo conectar a la base de datos: {str(e)}')
    
    return render(request, 'automatizacion/edit_process.html', context)

def load_process_columns(request, process_id):
    """Vista AJAX para cargar columnas de hojas de Excel seleccionadas"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Método no permitido'}, status=405)
    
    process = get_object_or_404(MigrationProcess, pk=process_id)
    
    if process.source.source_type != 'excel':
        return JsonResponse({'error': 'Este proceso no es de tipo Excel'}, status=400)
    
    try:
        import json
        data = json.loads(request.body)
        selected_sheets = data.get('selected_sheets', [])
        
        if not selected_sheets:
            return JsonResponse({'error': 'No se especificaron hojas'}, status=400)
        
        from .utils import ExcelProcessor
        processor = ExcelProcessor(process.source.file_path)
        
        sheets_columns = {}
        for sheet_name in selected_sheets:
            try:
                columns = processor.get_columns(sheet_name)
                sheets_columns[sheet_name] = columns
            except Exception as e:
                sheets_columns[sheet_name] = []
        
        return JsonResponse({
            'success': True,
            'sheets_columns': sheets_columns
        })
        
    except Exception as e:
        return JsonResponse({
            'error': f'Error cargando columnas: {str(e)}'
        }, status=500)
