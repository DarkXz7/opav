# 📘 IMPLEMENTACIÓN: Sincronización de Procesos con SQL Server

## 🎯 Objetivo

Sincronizar automáticamente los procesos de Django (`MigrationProcess`) con una tabla centralizada en SQL Server (`dbo.ProcesosGuardados`), permitiendo:
- ✅ Trazabilidad completa desde SQL Server
- ✅ Consultas directas sin pasar por Django
- ✅ Auditoría de creación, modificación y ejecución
- ✅ Centralización de metadatos de procesos

---

## 📦 Archivos Creados/Modificados

### ✅ Archivos NUEVOS:

1. **`automatizacion/process_sync.py`** (330 líneas)
   - Funciones helper para sincronización
   - `sync_process_to_sqlserver()`: Inserta o actualiza procesos
   - `update_ultima_ejecucion()`: Actualiza timestamp de ejecución
   - `delete_process_from_sqlserver()`: Eliminación lógica/física
   - `normalize_process_name()`: Limpia nombres de caracteres especiales

2. **`automatizacion/management/commands/sync_processes_to_sqlserver.py`** (140 líneas)
   - Comando Django para migración inicial
   - Sincroniza todos los procesos existentes
   - Soporta modo `--dry-run` para simulación
   - Soporta `--force` para forzar actualizaciones

3. **`automatizacion/management/__init__.py`** 
4. **`automatizacion/management/commands/__init__.py`**
   - Archivos de estructura de paquete

### 📝 Archivos MODIFICADOS:

1. **`proyecto_automatizacion/settings.py`**
   - Agregado alias de conexión `'sqlserver'` apuntando a `DestinoAutomatizacion`
   
2. **`automatizacion/models.py`**
   - **Modelo nuevo**: `ProcesosGuardados` (managed=False, espejo de tabla SQL)
   - **Método nuevo**: `MigrationProcess.save()` con sincronización automática
   - **Método modificado**: `MigrationProcess.run()` actualiza `UltimaEjecucion`

---

## 🗂️ Estructura de la Tabla SQL Server

La tabla **`dbo.ProcesosGuardados`** debe existir en la base `DestinoAutomatizacion` con este esquema:

```sql
CREATE TABLE dbo.ProcesosGuardados (
    Id INT IDENTITY(1,1) PRIMARY KEY,
    NombreProceso NVARCHAR(255) NOT NULL,
    TipoFuente NVARCHAR(50) NOT NULL,              -- 'Excel' o 'SQL'
    Fuente NVARCHAR(255) NULL,                     -- Ruta del archivo o conexión
    HojaTabla NVARCHAR(255) NULL,                  -- Nombre de la hoja o tabla procesada
    Destino NVARCHAR(255) NULL,                    -- Base o tabla destino
    Estado NVARCHAR(50) DEFAULT 'Activo',          -- Estado lógico del proceso
    FechaCreacion DATETIME DEFAULT GETDATE(),
    FechaActualizacion DATETIME NULL,
    UsuarioCreador NVARCHAR(255) NULL,
    Descripcion NVARCHAR(MAX) NULL,
    UltimaEjecucion DATETIME NULL,
    Version INT DEFAULT 1,
    Observaciones NVARCHAR(MAX) NULL
);

-- Crear índice único en NombreProceso para evitar duplicados
CREATE UNIQUE INDEX UX_ProcesosGuardados_Nombre 
ON dbo.ProcesosGuardados(NombreProceso);
```

> ⚠️ **IMPORTANTE**: Esta tabla debe crearse ANTES de usar la sincronización.

---

## 🔧 Configuración

### 1. Verificar conexión en `settings.py`

```python
DATABASES = {
    # ... otras bases de datos ...
    
    'sqlserver': {
        'ENGINE': 'mssql',
        'NAME': 'DestinoAutomatizacion',
        'USER': 'miguel',
        'PASSWORD': '16474791@',
        'HOST': 'localhost\\SQLEXPRESS',
        'PORT': '',
        'OPTIONS': {
            'driver': 'ODBC Driver 17 for SQL Server',
            'unicode_results': True,
            'host_is_server': True,
        },
    }
}
```

### 2. Crear la tabla en SQL Server

Ejecuta el script SQL anterior en SQL Server Management Studio (SSMS) o Azure Data Studio:

```powershell
# Conectar a SQL Server
sqlcmd -S localhost\SQLEXPRESS -U miguel -P "16474791@" -d DestinoAutomatizacion -Q "CREATE TABLE dbo.ProcesosGuardados (...)"
```

### 3. Migrar procesos existentes

Si ya tienes procesos en Django, sincronízalos todos de una vez:

```powershell
# Simular la sincronización (no hace cambios)
python manage.py sync_processes_to_sqlserver --dry-run

# Ejecutar la sincronización real
python manage.py sync_processes_to_sqlserver

# Forzar actualización de todos (sobrescribe datos)
python manage.py sync_processes_to_sqlserver --force
```

---

## 🚀 Uso Automático

### Creación de Procesos

Cuando creas un proceso en Django, **automáticamente** se sincroniza con SQL Server:

```python
# En tu código Django o desde el admin
proceso = MigrationProcess.objects.create(
    name="Mi Nuevo Proceso",
    description="Migración de datos de clientes",
    source=mi_fuente,
    # ... otros campos ...
)

# ✅ Después del save(), el proceso YA ESTÁ en SQL Server
```

**Terminal mostrará:**
```
✅ Sincronización SQL Server exitosa: Proceso 'Mi_Nuevo_Proceso' creado exitosamente en SQL Server (ID: 42)
```

### Edición de Procesos

Cuando modificas un proceso existente:

```python
proceso = MigrationProcess.objects.get(name="Mi Proceso")
proceso.description = "Descripción actualizada"
proceso.selected_tables = ['Clientes', 'Ventas']
proceso.save()

# ✅ La actualización se refleja en SQL Server con nueva versión
```

**Terminal mostrará:**
```
✅ Sincronización SQL Server exitosa: Proceso 'Mi_Proceso' actualizado exitosamente (ID: 42, Versión: 2)
```

### Ejecución de Procesos

Cuando ejecutas un proceso:

```python
proceso.run()

# ✅ El campo UltimaEjecucion se actualiza automáticamente
```

**Terminal mostrará:**
```
✅ UltimaEjecucion actualizada en SQL Server
```

---

## 🔍 Consultas Directas en SQL Server

Una vez sincronizados, puedes consultar los procesos directamente desde SQL Server:

### Ver todos los procesos activos:

```sql
SELECT 
    Id,
    NombreProceso,
    TipoFuente,
    Estado,
    FechaCreacion,
    UltimaEjecucion,
    Version
FROM dbo.ProcesosGuardados
WHERE Estado = 'Activo'
ORDER BY FechaCreacion DESC;
```

### Ver procesos ejecutados recientemente:

```sql
SELECT 
    NombreProceso,
    TipoFuente,
    UltimaEjecucion,
    DATEDIFF(HOUR, UltimaEjecucion, GETDATE()) AS HorasDesdeEjecucion
FROM dbo.ProcesosGuardados
WHERE UltimaEjecucion IS NOT NULL
ORDER BY UltimaEjecucion DESC;
```

### Ver historial de versiones:

```sql
SELECT 
    NombreProceso,
    Version,
    FechaActualizacion,
    Observaciones
FROM dbo.ProcesosGuardados
WHERE NombreProceso = 'Mi_Proceso'
ORDER BY Version DESC;
```

### Ver procesos por tipo de fuente:

```sql
SELECT 
    TipoFuente,
    COUNT(*) AS TotalProcesos,
    SUM(CASE WHEN Estado = 'Activo' THEN 1 ELSE 0 END) AS Activos,
    SUM(CASE WHEN UltimaEjecucion IS NOT NULL THEN 1 ELSE 0 END) AS ConEjecuciones
FROM dbo.ProcesosGuardados
GROUP BY TipoFuente;
```

---

## ⚙️ Flujo de Sincronización

### Diagrama de Flujo

```
┌─────────────────────────────────────────────────────────────┐
│ Usuario crea/edita proceso en Django (Frontend o Admin)   │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│ MigrationProcess.save() se ejecuta automáticamente         │
│   1. Guarda en Django (SQLite)                             │
│   2. Llama a sync_process_to_sqlserver()                   │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│ sync_process_to_sqlserver() [en process_sync.py]          │
│   1. Normaliza el nombre del proceso                       │
│   2. Extrae información (fuente, tipo, destino, etc.)      │
│   3. Verifica si ya existe en SQL Server (por nombre)      │
│   4a. Si existe → UPDATE + incrementa versión              │
│   4b. Si no existe → INSERT nuevo registro                 │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│ Base de datos: DestinoAutomatizacion                       │
│ Tabla: dbo.ProcesosGuardados                               │
│ ✅ Registro insertado/actualizado                           │
└─────────────────────────────────────────────────────────────┘
```

### Cuando se ejecuta un proceso:

```
┌─────────────────────────────────────────────────────────────┐
│ Usuario ejecuta proceso: proceso.run()                      │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│ MigrationProcess.run()                                      │
│   1. Marca status = 'running'                               │
│   2. Actualiza last_run = timezone.now()                    │
│   3. Llama a save() → sincroniza con SQL                    │
│   4. Llama a update_ultima_ejecucion()                      │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│ update_ultima_ejecucion() [en process_sync.py]             │
│   UPDATE dbo.ProcesosGuardados                             │
│   SET UltimaEjecucion = <timestamp>                        │
│   WHERE NombreProceso = <nombre_normalizado>               │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│ Campo UltimaEjecucion actualizado en SQL Server            │
│ ✅ Trazabilidad de ejecución completa                       │
└─────────────────────────────────────────────────────────────┘
```

---

## 🧪 Pruebas

### Prueba 1: Crear un nuevo proceso

```python
# En Django shell: python manage.py shell

from automatizacion.models import MigrationProcess, DataSource

# Crear proceso de prueba
proceso_test = MigrationProcess.objects.create(
    name="Test Sincronización SQL",
    description="Proceso de prueba para validar sincronización",
    source=DataSource.objects.first(),  # Usar una fuente existente
    status='configured'
)

# Verificar en SQL Server:
# SELECT * FROM dbo.ProcesosGuardados WHERE NombreProceso = 'Test_Sincronizacion_SQL';
```

### Prueba 2: Actualizar proceso existente

```python
proceso_test.description = "Descripción actualizada desde Django"
proceso_test.save()

# Verificar versión incrementada:
# SELECT Version, Observaciones FROM dbo.ProcesosGuardados 
# WHERE NombreProceso = 'Test_Sincronizacion_SQL';
```

### Prueba 3: Ejecutar proceso

```python
proceso_test.run()

# Verificar UltimaEjecucion:
# SELECT UltimaEjecucion, FechaActualizacion 
# FROM dbo.ProcesosGuardados 
# WHERE NombreProceso = 'Test_Sincronizacion_SQL';
```

### Prueba 4: Sincronización masiva

```powershell
# Migrar todos los procesos existentes
python manage.py sync_processes_to_sqlserver

# Verificar cantidad:
# SELECT COUNT(*) FROM dbo.ProcesosGuardados;
```

---

## 🐛 Troubleshooting

### Error: "No module named 'process_sync'"

**Causa**: El módulo `process_sync.py` no está en el lugar correcto.

**Solución**:
```powershell
# Verificar que existe el archivo:
ls automatizacion/process_sync.py
```

### Error: "Invalid object name 'dbo.ProcesosGuardados'"

**Causa**: La tabla no existe en SQL Server.

**Solución**:
```sql
-- Ejecutar en SQL Server:
USE DestinoAutomatizacion;
GO
CREATE TABLE dbo.ProcesosGuardados (...);
```

### Advertencia: "No se pudo sincronizar con SQL Server"

**Causa**: Error en la conexión a SQL Server.

**Solución**:
```powershell
# Verificar configuración en settings.py
# Probar conexión directa:
python manage.py dbshell --database=sqlserver
```

### Los procesos no se sincronizan automáticamente

**Causa**: El método `save()` personalizado no se está ejecutando.

**Solución**:
```python
# Verificar que estás usando .save(), no .update():
proceso.description = "Nueva descripción"
proceso.save()  # ✅ Correcto

# NO usar:
MigrationProcess.objects.filter(id=proceso.id).update(description="...") # ❌ No llama a save()
```

---

## 📊 Estadísticas y Reportes

### Dashboard de Procesos (SQL)

```sql
-- Vista general de procesos
WITH EstadisticasProcesos AS (
    SELECT 
        TipoFuente,
        Estado,
        COUNT(*) AS Cantidad,
        MAX(UltimaEjecucion) AS UltimaEjecucionGrupo
    FROM dbo.ProcesosGuardados
    GROUP BY TipoFuente, Estado
)
SELECT 
    TipoFuente AS 'Tipo de Fuente',
    SUM(CASE WHEN Estado = 'Activo' THEN Cantidad ELSE 0 END) AS 'Activos',
    SUM(CASE WHEN Estado = 'Completado' THEN Cantidad ELSE 0 END) AS 'Completados',
    SUM(CASE WHEN Estado = 'Fallido' THEN Cantidad ELSE 0 END) AS 'Fallidos',
    SUM(Cantidad) AS 'Total'
FROM EstadisticasProcesos
GROUP BY TipoFuente
ORDER BY TipoFuente;
```

---

## ✅ Checklist de Implementación

- [✅] Alias 'sqlserver' agregado en `settings.py`
- [✅] Modelo `ProcesosGuardados` creado (managed=False)
- [✅] Módulo `process_sync.py` con funciones helper
- [✅] Método `save()` modificado en `MigrationProcess`
- [✅] Método `run()` actualiza `UltimaEjecucion`
- [✅] Comando `sync_processes_to_sqlserver` creado
- [ ] Tabla `dbo.ProcesosGuardados` creada en SQL Server ⚠️
- [ ] Migración inicial ejecutada
- [ ] Pruebas end-to-end completadas

---

## 📝 Notas Finales

1. **La sincronización NO bloquea el save de Django**: Si SQL Server falla, el proceso igual se guarda en Django (robustez).

2. **Nombres normalizados**: Los nombres de procesos se limpian automáticamente (sin espacios, caracteres especiales).

3. **Versionado automático**: Cada actualización incrementa el campo `Version`.

4. **Soft delete**: Por defecto, los procesos eliminados se marcan como "Eliminado" (no se borran físicamente).

5. **Compatibilidad total**: No afecta el procesamiento de datos existente, solo agrega capa de sincronización.

---

¡Implementación completa! 🎉
