# 📊 DÓNDE SE GUARDAN LOS PROCESOS

## 🗄️ Ubicación Principal

Los procesos se guardan en una **base de datos SQLite**:

```
📁 proyecto_automatizacion/
   └─ db.sqlite3  ← AQUÍ SE GUARDAN LOS PROCESOS
```

**Ruta completa:**
```
C:\Users\migue\OneDrive\Escritorio\DJANGO DE NUEVO\opav\proyecto_automatizacion\db.sqlite3
```

---

## 📋 Estructura de Almacenamiento

### **1. Tabla Principal: `automatizacion_migrationprocess`**

Cada proceso guardado es una **fila** en esta tabla con estos campos:

```sql
CREATE TABLE automatizacion_migrationprocess (
    id                   INTEGER PRIMARY KEY,
    name                 VARCHAR(255) UNIQUE,
    description          TEXT,
    source_id            INTEGER,              -- FK a DataSource
    selected_sheets      JSON,                 -- ['Hoja 1', 'Hoja 2']
    selected_database    VARCHAR(100),         -- 'ProyectoMiguel'
    selected_tables      JSON,                 -- ['dbo.Usuarios', 'dbo.Productos']
    selected_columns     JSON,                 -- {'dbo.Usuarios': ['ID', 'Nombre']}
    target_db_name       VARCHAR(100),         -- 'DestinoAutomatizacion'
    target_db_connection INTEGER,              -- FK a DatabaseConnection
    target_table         VARCHAR(100),
    status               VARCHAR(20),          -- 'draft', 'completed', etc.
    created_at           DATETIME,
    updated_at           DATETIME,             -- NUEVO campo
    last_run             DATETIME,
    allow_rollback       BOOLEAN,
    last_checkpoint      JSON
);
```

---

## 🔗 Tablas Relacionadas

### **2. Tabla `automatizacion_datasource`**
Almacena información sobre el origen de datos:

```sql
CREATE TABLE automatizacion_datasource (
    id             INTEGER PRIMARY KEY,
    name           VARCHAR(255),
    source_type    VARCHAR(20),      -- 'excel', 'csv', 'sql'
    file_path      VARCHAR(255),     -- Ruta al archivo Excel/CSV
    connection_id  INTEGER,          -- FK a DatabaseConnection (para SQL)
    created_at     DATETIME
);
```

### **3. Tabla `automatizacion_databaseconnection`**
Almacena conexiones a bases de datos SQL:

```sql
CREATE TABLE automatizacion_databaseconnection (
    id                  INTEGER PRIMARY KEY,
    name                VARCHAR(100) UNIQUE,
    server              VARCHAR(255),         -- 'localhost,1433'
    username            VARCHAR(100),
    password            VARCHAR(255),
    port                INTEGER,              -- 1433
    selected_database   VARCHAR(100),         -- 'ProyectoMiguel'
    available_databases JSON,
    created_at          DATETIME,
    last_used           DATETIME
);
```

---

## 📊 Ejemplo de Datos Guardados

### **Proceso "arbejas" (ID: 34)**

```json
{
    "id": 34,
    "name": "arbejas",
    "description": "",
    "source_id": 9,
    "selected_sheets": null,
    "selected_database": null,
    "selected_tables": ["dbo.AutomatizacionTestTable"],
    "selected_columns": {
        "dbo.AutomatizacionTestTable": ["Nombre", "FechaCreacion"]
    },
    "target_db_name": "DestinoAutomatizacion",
    "target_db_connection": null,
    "target_table": null,
    "status": "completed",
    "created_at": "2025-10-06 14:12:49",
    "updated_at": "2025-10-08 19:20:22",  // ← Se actualiza al editar
    "last_run": "2025-10-06 15:15:49",
    "allow_rollback": true,
    "last_checkpoint": null
}
```

---

## 📁 Archivos Excel/CSV

Los archivos físicos se guardan en:

```
📁 proyecto_automatizacion/
   ├─ db.sqlite3                    ← Metadatos del proceso
   ├─ temp_multihoja_test.xlsx      ← Archivo Excel
   ├─ test_limpieza.xlsx            ← Otro archivo Excel
   └─ uploads/                      ← Carpeta de archivos subidos
      └─ archivo.xlsx
```

**Nota**: La ruta del archivo se guarda en `datasource.file_path`

---

## 🔍 Cómo se Recuperan los Procesos

### **En la vista `list_processes()`:**

```python
# 1. Consulta a la base de datos
processes = MigrationProcess.objects.all().order_by('-updated_at')

# 2. Django ejecuta esta SQL:
SELECT * FROM automatizacion_migrationprocess 
ORDER BY updated_at DESC;

# 3. Devuelve objetos Python:
for process in processes:
    print(process.name)           # 'arbejas'
    print(process.selected_tables) # ['dbo.AutomatizacionTestTable']
    print(process.selected_columns) # {'dbo.AutomatizacionTestTable': [...]}
```

### **En la vista `view_process()`:**

```python
# 1. Obtener proceso específico
process = MigrationProcess.objects.get(id=34)

# 2. Django ejecuta:
SELECT * FROM automatizacion_migrationprocess 
WHERE id = 34;

# 3. Cargar relaciones (DataSource, DatabaseConnection)
# Django hace JOINs automáticos:
SELECT * FROM automatizacion_datasource WHERE id = process.source_id;
SELECT * FROM automatizacion_databaseconnection WHERE id = source.connection_id;
```

---

## 📊 Estadísticas Actuales

```
Total de procesos guardados: 36

Por tipo:
├─ Excel: 27 procesos
└─ SQL:   9 procesos

Estado:
├─ Completados: 15
├─ Borradores:  12
└─ Fallidos:    9
```

---

## 🛠️ Herramientas para Ver los Datos

### **1. DB Browser for SQLite** (Recomendado)
- Descarga: https://sqlitebrowser.org/
- Abre: `db.sqlite3`
- Navega a tabla: `automatizacion_migrationprocess`

### **2. Línea de comandos SQLite:**
```bash
cd "C:\Users\migue\OneDrive\Escritorio\DJANGO DE NUEVO\opav\proyecto_automatizacion"
sqlite3 db.sqlite3

# Ver todos los procesos
SELECT id, name, status, created_at FROM automatizacion_migrationprocess;

# Ver proceso específico
SELECT * FROM automatizacion_migrationprocess WHERE name = 'arbejas';
```

### **3. Django Shell:**
```bash
python manage.py shell

# En el shell:
from automatizacion.models import MigrationProcess
processes = MigrationProcess.objects.all()
for p in processes:
    print(f"{p.id}: {p.name} - {p.status}")
```

---

## 🔄 Flujo de Guardado

```
1. Usuario crea proceso en el frontend
                ↓
2. POST a /automatizacion/save_process/
                ↓
3. Django crea objeto MigrationProcess
                ↓
4. Django ejecuta INSERT INTO automatizacion_migrationprocess
                ↓
5. SQLite guarda en db.sqlite3
                ↓
6. Django asigna ID auto-increment
                ↓
7. Retorna al frontend con ID del proceso
```

---

## 📝 Resumen

| Componente | Ubicación | Qué Guarda |
|------------|-----------|------------|
| **Base de datos** | `db.sqlite3` | Todos los metadatos de procesos |
| **Tabla procesos** | `automatizacion_migrationprocess` | Configuración de cada proceso |
| **Tabla fuentes** | `automatizacion_datasource` | Información de origen (Excel/SQL) |
| **Tabla conexiones** | `automatizacion_databaseconnection` | Credenciales SQL Server |
| **Archivos Excel** | Sistema de archivos | Archivos físicos .xlsx/.csv |
| **Logs Excel** | `automatizacion_migrationlog` | Historial de ejecuciones Excel |
| **Logs SQL** | SQL Server `LogsAutomatizacion.dbo.ProcesoLog` | Historial de ejecuciones SQL |

---

## 🎯 Para Ver Tu Proceso "arbejas"

```python
python manage.py shell

from automatizacion.models import MigrationProcess
p = MigrationProcess.objects.get(name='arbejas')

print(f"ID: {p.id}")
print(f"Tablas: {p.selected_tables}")
print(f"Columnas: {p.selected_columns}")
print(f"Creado: {p.created_at}")
print(f"Modificado: {p.updated_at}")
```

**Resultado:**
```
ID: 34
Tablas: ['dbo.AutomatizacionTestTable']
Columnas: {'dbo.AutomatizacionTestTable': ['Nombre', 'FechaCreacion']}
Creado: 2025-10-06 14:12:49
Modificado: 2025-10-08 19:20:22
```
