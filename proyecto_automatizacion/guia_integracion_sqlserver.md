# Guía de Integración con SQL Server Express

Esta guía detalla todos los pasos necesarios para configurar y probar la integración entre Django y SQL Server Express para el registro de procesos.

> **¡IMPORTANTE!** Ahora todos los procesos web se registrarán automáticamente en SQL Server. Se ha implementado un sistema completo de logging que captura información sobre las operaciones realizadas en la aplicación.

## 1. Requisitos Previos

- SQL Server Express instalado y en ejecución
- Base de datos `LogsAutomatizacion` creada
- Driver ODBC 17 para SQL Server instalado
- Paquetes de Python instalados:
  - `django-mssql-backend`
  - `pyodbc`

## 2. Estructura de la Base de Datos

### Tabla ProcesoLog

La tabla `ProcesoLog` debe tener la siguiente estructura:

```sql
USE LogsAutomatizacion;

IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'ProcesoLog')
CREATE TABLE ProcesoLog (
    ProcesoID INT IDENTITY(1,1) PRIMARY KEY,
    FechaEjecucion DATETIME NOT NULL,
    Estado VARCHAR(100) NOT NULL,
    ParametrosEntrada NVARCHAR(MAX) NULL,
    DuracionSegundos FLOAT NULL,
    ErrorDetalle NVARCHAR(MAX) NULL
);
```

## 3. Archivos del Proyecto

### settings.py

La configuración de la base de datos en `settings.py` incluye tanto la base de datos predeterminada (SQLite) como la conexión a SQL Server Express:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    },
    'logs': {
        'ENGINE': 'sql_server.pyodbc',
        'NAME': 'LogsAutomatizacion',
        'USER': 'miguel',
        'PASSWORD': '16474791@',
        'HOST': 'localhost\\SQLEXPRESS',  # Instancia nombrada de SQL Express
        'PORT': '',                      # Dejamos el puerto vacío para instancias nombradas
        'OPTIONS': {
            'driver': 'ODBC Driver 17 for SQL Server',
            'unicode_results': True,
            'host_is_server': True,
        },
    }
}
```

### models_logs.py

El modelo `ProcesoLog` mapea la tabla existente en SQL Server:

```python
from django.db import models

class ProcesoLog(models.Model):
    """
    Modelo para almacenar registros de logs de procesos en SQL Server Express
    Mapea a la tabla existente 'ProcesoLog' en la base de datos 'LogsAutomatizacion'
    """
    ProcesoID = models.AutoField(primary_key=True)
    FechaEjecucion = models.DateTimeField()
    Estado = models.CharField(max_length=100)
    ParametrosEntrada = models.TextField(null=True, blank=True)
    DuracionSegundos = models.FloatField(null=True, blank=True)
    ErrorDetalle = models.TextField(null=True, blank=True)
    
    class Meta:
        managed = False  # Django no gestiona esta tabla (ya existe)
        db_table = 'ProcesoLog'  # Nombre exacto de la tabla en SQL Server
        app_label = 'automatizacion'
        verbose_name = 'Log de Proceso'
        verbose_name_plural = 'Logs de Procesos'
    
    def __str__(self):
        return f"Proceso {self.ProcesoID}: {self.Estado} ({self.FechaEjecucion})"
```

### logs/utils.py

Utilidades para registrar procesos en SQL Server:

```python
"""
Utilidades para el registro de procesos en SQL Server
Facilita el registro de eventos en la tabla ProcesoLog
"""

import datetime
import json
import time
from automatizacion.models_logs import ProcesoLog

class ProcesoLogger:
    """
    Clase para gestionar el registro de procesos en la tabla ProcesoLog
    Permite registrar inicio, fin, éxito y error de procesos
    """
    
    def __init__(self, nombre_proceso):
        # Ver implementación en el archivo
        pass
    
    def iniciar(self, parametros=None):
        # Ver implementación en el archivo
        pass
    
    def finalizar_exito(self, detalles=None):
        # Ver implementación en el archivo
        pass
    
    def finalizar_error(self, error):
        # Ver implementación en el archivo
        pass


def registrar_evento(nombre_evento, estado, parametros=None, error=None):
    # Ver implementación en el archivo
    pass
```

## 4. Pruebas de Integración

### Script de Prueba Básico

Para probar la inserción y consulta básica:

**En PowerShell:**
```powershell
Get-Content test_proceso_log.py | python manage.py shell
```

**En CMD:**
```cmd
python manage.py shell < test_proceso_log.py
```

### Script de Prueba Completo

Para probar todas las funcionalidades del logger:

**En PowerShell:**
```powershell
Get-Content test_proceso_log_completo.py | python manage.py shell
```

**En CMD:**
```cmd
python manage.py shell < test_proceso_log_completo.py
```

## 5. Verificación en SQL Server Management Studio (SSMS)

Para verificar los datos en SSMS, consulte el archivo `verificacion_ssms.md`.

## 6. Uso en el Proyecto

### Registro Simple de un Evento

```python
from automatizacion.logs.utils import registrar_evento

# Registrar un evento simple
registrar_evento(
    nombre_evento="Migración de datos completada", 
    estado="Completado", 
    parametros={"tabla_origen": "Clientes", "registros_migrados": 150}
)
```

### Registro de un Proceso Completo

```python
from automatizacion.logs.utils import ProcesoLogger

# Iniciar el logger para un proceso
logger = ProcesoLogger("Migración de Productos")
proceso_id = logger.iniciar(parametros={"origen": "Excel", "archivo": "productos.xlsx"})

try:
    # Realizar el proceso...
    # ...código de migración...
    
    # Registrar éxito
    logger.finalizar_exito(f"Migración exitosa: 120 productos importados")
    
except Exception as e:
    # Registrar error
    logger.finalizar_error(f"Error en la migración: {str(e)}")
    raise
```

## 7. Consulta de Logs en la Interfaz Web

Se ha añadido una interfaz web para consultar los logs almacenados en SQL Server:

1. Accede a la opción "Registros SQL" en el menú de navegación
2. Utiliza los filtros para buscar registros específicos
3. Haz clic en "Detalle" para ver información completa de un registro

Esta interfaz permite:
- Ver todos los procesos registrados
- Filtrar por estado o ID de proceso
- Ver detalles completos de cada registro
- Acceder a información de errores
- Navegar por los registros con paginación

## 8. Solución de Problemas

### Problemas de Conexión

1. Verificar que SQL Server Express está en ejecución
2. Confirmar credenciales (usuario/contraseña)
3. Verificar nombre de instancia (`localhost\SQLEXPRESS`)
4. Verificar que el driver ODBC está correctamente instalado

### Verificar Driver ODBC

```bash
python -c "import pyodbc; print([x for x in pyodbc.drivers() if 'SQL Server' in x])"
```

### Verificar Base de Datos

En SSMS o mediante código:

```sql
SELECT name FROM sys.databases WHERE name = 'LogsAutomatizacion';
```

### Verificar Tabla

```sql
USE LogsAutomatizacion;
SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'ProcesoLog';
```
