# 🔧 Corrección: Historial de Ejecuciones en Procesos SQL Server

## 📋 Problema Identificado

### Síntoma
En la vista de detalles de un proceso (`/automatizacion/process/<id>/`), el historial de ejecuciones mostraba **TODOS** los logs de **TODOS** los procesos de manera global cuando el proceso era de tipo SQL Server.

### Comportamiento Correcto vs Incorrecto

| Tipo de Proceso | Comportamiento ANTES | Comportamiento ESPERADO |
|-----------------|----------------------|-------------------------|
| **Excel/CSV** | ✅ Muestra solo logs del proceso específico | ✅ Correcto |
| **SQL Server** | ❌ Muestra logs de TODOS los procesos | ✅ Debe mostrar solo logs del proceso específico |

---

## 🔍 Causa Raíz

El sistema tiene **DOS sistemas de logging diferentes**:

### 1. **MigrationLog** (Modelo Django - para Excel/CSV)
- Tabla gestionada por Django ORM
- Tiene relación ForeignKey con `MigrationProcess`
- Se consulta mediante: `process.logs.all()`
- ✅ Filtra automáticamente por proceso

### 2. **ProcesoLog** (Tabla SQL Server - para procesos SQL)
- Tabla existente en SQL Server (no gestionada por Django)
- Ubicación: Base de datos `LogsAutomatizacion`
- **NO tiene relación directa con MigrationProcess**
- Campos clave:
  - `LogID`: Primary key autoincremental
  - `ProcesoID`: UUID de la ejecución específica
  - `MigrationProcessID`: FK opcional al proceso configurado
  - `NombreProceso`: Nombre del proceso
  - `FechaEjecucion`: Timestamp de ejecución
  - `Estado`: Estado del proceso
  - `DuracionSegundos`: Duración en segundos
  - `MensajeError`: Mensaje de error (si existe)

### El Problema
La vista `view_process()` **siempre** usaba `process.logs.all()` para todos los tipos de proceso, pero para procesos SQL, esto no funciona porque `ProcessTracker` escribe en `ProcesoLog`, no en `MigrationLog`.

---

## ✅ Solución Implementada

### 1. **Modificación en `views.py`** - Función `view_process()`

**Antes:**
```python
def view_process(request, process_id):
    process = get_object_or_404(MigrationProcess, pk=process_id)
    logs = process.logs.all().order_by('-timestamp')[:10]  # ❌ No funciona para SQL
    # ...
```

**Después:**
```python
def view_process(request, process_id):
    process = get_object_or_404(MigrationProcess, pk=process_id)
    
    # 🔧 CORRECCIÓN: Diferenciar por tipo de proceso
    if process.source.source_type == 'sql':
        from automatizacion.logs.models_logs import ProcesoLog
        from django.db.models import Q
        
        # ✅ Filtrar por MigrationProcessID o nombre del proceso
        logs = ProcesoLog.objects.filter(
            Q(MigrationProcessID=process.id) | Q(NombreProceso=process.name)
        ).order_by('-FechaEjecucion')[:10]
        
        context = {
            'process': process,
            'logs': logs,
            'connection': process.source.connection,
            'is_sql_process': True  # Flag para el template
        }
    else:
        # ✅ Para Excel/CSV usar MigrationLog
        logs = process.logs.all().order_by('-timestamp')[:10]
        context = {
            'process': process,
            'logs': logs,
            'file_path': process.source.file_path if hasattr(process.source, 'file_path') else None
        }
```

**Cambios clave:**
1. ✅ Detecta si el proceso es de tipo `sql`
2. ✅ Para SQL: consulta `ProcesoLog` filtrando por `MigrationProcessID` o `NombreProceso`
3. ✅ Para Excel/CSV: mantiene el comportamiento original
4. ✅ Agrega flag `is_sql_process` para que el template sepa qué campos mostrar

---

### 2. **Modificación en `view_process.html`** - Sección de Historial

**Cambios realizados:**

#### a) **Encabezados de tabla dinámicos**
```django
<thead>
    <tr>
        <th>Fecha</th>
        {% if is_sql_process %}
            <th>Estado</th>
            <th>Duración</th>
            <th>Proceso ID</th>
        {% else %}
            <th>Etapa</th>
            <th>Mensaje</th>
            <th>Filas</th>
            <th>Duración</th>
        {% endif %}
        <th>Nivel</th>
    </tr>
</thead>
```

#### b) **Filas de datos adaptadas a cada tipo**
```django
{% if is_sql_process %}
    {# Logs de ProcesoLog (SQL Server) #}
    <td>{{ log.FechaEjecucion|date:"d/m/Y H:i:s" }}</td>
    <td>
        <span class="badge {% if log.Estado == 'Completado exitosamente' %}bg-success{% elif 'Error' in log.Estado %}bg-danger{% else %}bg-info{% endif %}">
            {{ log.Estado }}
        </span>
    </td>
    <td>{{ log.DuracionSegundos }}s</td>
    <td><code>{{ log.ProcesoID|slice:":8" }}...</code></td>
    <td>
        {% if log.MensajeError %}
            <span class="badge bg-danger">Error</span>
            <button data-bs-toggle="tooltip" title="{{ log.MensajeError }}">
                <i class="fas fa-exclamation-circle"></i>
            </button>
        {% else %}
            <span class="badge bg-success">OK</span>
        {% endif %}
    </td>
{% else %}
    {# Logs de MigrationLog (Excel/CSV) - código original #}
    <td>{{ log.timestamp|date:"d/m/Y H:i:s" }}</td>
    <td><span class="badge bg-secondary">{{ log.get_stage_display }}</span></td>
    <td>{{ log.message|truncatechars:50 }}</td>
    <td>{{ log.rows_processed|default:"0" }}</td>
    <td>{{ log.duration_ms }}ms</td>
    <td>
        <span class="badge {% if log.level == 'success' %}bg-success{% elif log.level == 'error' %}bg-danger{% else %}bg-info{% endif %}">
            {{ log.get_level_display }}
        </span>
    </td>
{% endif %}
```

---

## 🎯 Campos Mostrados por Tipo de Proceso

### Para Procesos SQL Server (`ProcesoLog`)
| Campo | Descripción | Ejemplo |
|-------|-------------|---------|
| Fecha | `FechaEjecucion` | 08/10/2025 15:30:00 |
| Estado | `Estado` | "Completado exitosamente" / "Error en ejecución" |
| Duración | `DuracionSegundos` | 45s |
| Proceso ID | `ProcesoID` (primeros 8 caracteres) | `a1b2c3d4...` |
| Nivel | Badge según `MensajeError` | ✅ OK / ❌ Error |

### Para Procesos Excel/CSV (`MigrationLog`)
| Campo | Descripción | Ejemplo |
|-------|-------------|---------|
| Fecha | `timestamp` | 08/10/2025 15:30:00 |
| Etapa | `stage` | "Carga de datos" |
| Mensaje | `message` | "Procesando archivo..." |
| Filas | `rows_processed` | 1000 |
| Duración | `duration_ms` | 250ms |
| Nivel | `level` | Info / Success / Error |

---

## 📝 Resumen de Archivos Modificados

1. **`automatizacion/views.py`**
   - Función `view_process()` - Líneas 57-82
   - Lógica diferenciada por tipo de proceso

2. **`proyecto_automatizacion/templates/automatizacion/view_process.html`**
   - Sección "Historial de Ejecuciones" - Líneas 267-362
   - Template dinámico según `is_sql_process`

---

## 🧪 Pruebas Recomendadas

### Proceso SQL Server
1. Ir a un proceso SQL: `/automatizacion/process/<id>/`
2. Verificar que el historial muestre **solo** las ejecuciones de ese proceso
3. Verificar que se muestren campos: Fecha, Estado, Duración, Proceso ID, Nivel
4. Ejecutar el proceso
5. Recargar la página
6. Verificar que aparezca el nuevo log **solo para ese proceso**

### Proceso Excel/CSV
1. Ir a un proceso Excel: `/automatizacion/process/<id>/`
2. Verificar que el historial siga funcionando correctamente
3. Verificar que se muestren campos: Fecha, Etapa, Mensaje, Filas, Duración, Nivel
4. Ejecutar el proceso
5. Verificar que el log se actualice correctamente

---

## ⚠️ Notas Importantes

### Migración de Datos (Opcional)
Para mejorar la precisión del filtrado, se recomienda actualizar `ProcessTracker` para que siempre establezca `MigrationProcessID` al crear logs:

```python
# En process_tracker.py, método crear_registro()
def crear_registro(self, migration_process_id=None):
    with transaction.atomic():
        self._registro = self.ProcesoLog.objects.create(
            ProcesoID=self.proceso_id,
            MigrationProcessID=migration_process_id,  # ← IMPORTANTE
            NombreProceso=self.nombre_proceso,
            # ...
        )
```

### Filtrado Actual
La consulta actual usa `Q(MigrationProcessID=process.id) | Q(NombreProceso=process.name)`:
- ✅ Filtra por `MigrationProcessID` (más preciso)
- ✅ Fallback a `NombreProceso` (para logs antiguos)
- ⚠️ Si hay procesos con el mismo nombre, podrían mezclarse

---

## ✅ Resultado Final

### Antes (❌ Incorrecto)
```
Proceso: "Migración Clientes SQL" (ID: 10)
Historial:
  - Migración Productos SQL (ID: 15)  ← No debería aparecer
  - Migración Clientes SQL (ID: 10)   ✓
  - Migración Ventas SQL (ID: 20)     ← No debería aparecer
  - Migración Clientes SQL (ID: 10)   ✓
```

### Después (✅ Correcto)
```
Proceso: "Migración Clientes SQL" (ID: 10)
Historial:
  - Migración Clientes SQL (ID: 10)   ✓
  - Migración Clientes SQL (ID: 10)   ✓
  - Migración Clientes SQL (ID: 10)   ✓
```

---

**Fecha de Corrección:** 8 de Octubre, 2025  
**Estado:** ✅ Implementado y listo para pruebas
