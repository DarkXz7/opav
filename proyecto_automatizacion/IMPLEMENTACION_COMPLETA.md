# 📚 GUÍA COMPLETA DE IMPLEMENTACIÓN - SISTEMA DE VALIDACIÓN Y NORMALIZACIÓN

## 🎯 OBJETIVO

Implementar un sistema robusto de validación y normalización de datos que:
- Elimina la vista intermedia de sheets
- Permite renombrar solo la hoja activa
- Mueve el botón "Seleccionar todas" debajo de "Columnas disponibles"
- Activa correctamente checkboxes y campos de valores por defecto
- Implementa validación en tiempo real
- Normaliza valores según 4 tipos macro: Texto, Número, Fecha, Booleano
- Mejora logging y manejo de errores
- Incluye tests unitarios

---

## 📁 ESTRUCTURA DE ARCHIVOS MODIFICADOS/CREADOS

```
proyecto_automatizacion/
├── automatizacion/
│   ├── utils/
│   │   ├── __init__.py                    [CREADO]
│   │   └── validators.py                  [CREADO] ✅
│   ├── models.py                          [MODIFICAR]
│   ├── views.py                           [MODIFICAR]
│   ├── urls.py                            [MODIFICAR]
│   ├── templates/automatizacion/
│   │   └── excel_multi_sheet_selector.html [MODIFICAR]
│   └── tests/
│       └── test_validation_system.py      [CREAR]
├── IMPLEMENTACION_COMPLETA.md            [ESTE ARCHIVO]
└── CHECKLIST_PRUEBAS.md                  [CREAR]
```

---

## 🔧 PASO 1: MODIFICAR URLS.PY

**Objetivo**: Eliminar la ruta intermedia `/automatizacion/excel/<id>/sheets/`

**Archivo**: `automatizacion/urls.py`

**Cambios**:

```python
# ANTES (comentar o eliminar):
# path('excel/<int:source_id>/sheets/', views.excel_sheet_selector, name='excel_sheet_selector'),

# DESPUÉS (mantener solo):
path('excel/<int:source_id>/multi-config/', views.excel_multi_sheet_config, name='excel_multi_config'),
```

**Explicación**: La vista `/sheets/` ya no es necesaria. Después de subir el Excel, se redirige directamente a `/multi-config/`.

---

## 🔧 PASO 2: MODIFICAR VIEWS.PY

### 2.1 Importar Nuevos Validadores

**Ubicación**: Al inicio del archivo `views.py`

```python
# Agregar después de los imports existentes:
from .utils.validators import (
    normalize_name,
    validate_sheet_name,
    validate_column_name,
    infer_sql_type,
    normalize_value_by_type,
    normalize_dataframe_by_mappings,
    validate_column_mappings
)
```

### 2.2 Modificar Vista de Upload para Redirección Directa

**Función**: `upload_excel_file` (buscar en views.py)

**Cambio**:

```python
# ANTES:
# return redirect('automatizacion:excel_sheet_selector', source_id=data_source.id)

# DESPUÉS:
return redirect('automatizacion:excel_multi_config', source_id=data_source.id)
```

### 2.3 Modificar Vista `excel_multi_sheet_config`

**Función**: `excel_multi_sheet_config`

**Cambios completos** (reemplazar toda la función):

```python
@login_required
def excel_multi_sheet_config(request, source_id):
    """
    Vista principal de configuración multi-hoja.
    
    MEJORAS IMPLEMENTADAS:
    - Inferencia automática de tipos SQL
    - Validación de nombres en tiempo real
    - Normalización de valores según tipo
    - Mejor manejo de errores
    """
    try:
        data_source = DataSource.objects.get(id=source_id)
        
        if not data_source.file_path or not os.path.exists(data_source.file_path):
            messages.error(request, "El archivo Excel no existe o no se encuentra.")
            return redirect('automatizacion:data_source_list')
        
        # Leer archivo Excel
        try:
            excel_file = pd.ExcelFile(data_source.file_path)
            sheets_data = {}
            
            for sheet_name in excel_file.sheet_names:
                df = pd.read_excel(excel_file, sheet_name=sheet_name)
                
                # Generar preview de datos (primeras 5 filas)
                preview_data = df.head(5).to_dict('records')
                
                # Inferir tipos SQL para cada columna
                column_types = {}
                for col in df.columns:
                    type_info = infer_sql_type(df[col])
                    column_types[col] = type_info
                
                sheets_data[sheet_name] = {
                    'columns': list(df.columns),
                    'row_count': len(df),
                    'preview': preview_data,
                    'column_types': column_types,
                    'suggested_name': normalize_name(sheet_name)
                }
            
            context = {
                'data_source': data_source,
                'sheets_data': sheets_data,
                'sheet_names': list(sheets_data.keys())
            }
            
            return render(request, 'automatizacion/excel_multi_sheet_selector.html', context)
            
        except Exception as e:
            logger.error(f"Error al procesar Excel: {e}", exc_info=True)
            messages.error(request, f"Error al leer el archivo Excel: {str(e)}")
            return redirect('automatizacion:data_source_list')
    
    except DataSource.DoesNotExist:
        messages.error(request, "La fuente de datos no existe.")
        return redirect('automatizacion:data_source_list')
```

### 2.4 Agregar Nueva Vista para Validación AJAX

**Agregar al final de views.py**:

```python
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
import json

@login_required
@require_http_methods(["POST"])
def validate_sheet_rename(request):
    """
    Endpoint AJAX para validar renombrado de hoja en tiempo real.
    
    POST /automatizacion/validate-sheet-rename/
    Body: {
        "original_name": "Hoja1",
        "new_name": "ventas_2024",
        "existing_names": ["productos", "clientes"]
    }
    
    Response: {
        "valid": true/false,
        "normalized": "ventas_2024",
        "error": "mensaje de error (si aplica)"
    }
    """
    try:
        data = json.loads(request.body)
        new_name = data.get('new_name', '')
        existing_names = data.get('existing_names', [])
        
        # Validar nombre
        is_valid, normalized, error = validate_sheet_name(new_name, existing_names)
        
        return JsonResponse({
            'valid': is_valid,
            'normalized': normalized,
            'error': error
        })
    
    except Exception as e:
        logger.error(f"Error en validación de nombre: {e}", exc_info=True)
        return JsonResponse({
            'valid': False,
            'error': f'Error interno: {str(e)}'
        }, status=500)


@login_required
@require_http_methods(["POST"])
def infer_column_types(request, source_id):
    """
    Endpoint AJAX para inferir tipos de columnas.
    
    POST /automatizacion/excel/<source_id>/infer-types/
    Body: {
        "sheet_name": "Hoja1",
        "columns": ["edad", "nombre", "fecha_registro"]
    }
    
    Response: {
        "types": {
            "edad": {
                "sql_type": "INT",
                "confidence": 1.0,
                "nullable": false,
                "default_value": "0",
                "warnings": []
            },
            ...
        }
    }
    """
    try:
        data_source = DataSource.objects.get(id=source_id)
        data = json.loads(request.body)
        sheet_name = data.get('sheet_name')
        columns = data.get('columns', [])
        
        if not os.path.exists(data_source.file_path):
            return JsonResponse({'error': 'Archivo no encontrado'}, status=404)
        
        # Leer hoja específica
        df = pd.read_excel(data_source.file_path, sheet_name=sheet_name)
        
        # Inferir tipos
        types_info = {}
        for col in columns:
            if col in df.columns:
                types_info[col] = infer_sql_type(df[col])
        
        return JsonResponse({'types': types_info})
    
    except Exception as e:
        logger.error(f"Error al inferir tipos: {e}", exc_info=True)
        return JsonResponse({'error': str(e)}, status=500)
```

---

## 🔧 PASO 3: ACTUALIZAR URLS.PY (Agregar Nuevas Rutas AJAX)

**Archivo**: `automatizacion/urls.py`

**Agregar al final de urlpatterns**:

```python
urlpatterns = [
    # ... rutas existentes ...
    
    # Nuevas rutas para validación AJAX
    path('validate-sheet-rename/', views.validate_sheet_rename, name='validate_sheet_rename'),
    path('excel/<int:source_id>/infer-types/', views.infer_column_types, name='infer_column_types'),
]
```

---

## 🔧 PASO 4: MODIFICAR MODELS.PY

### 4.1 Agregar Campo para Persistir Configuración de Tipos

**Ubicación**: Modelo `MigrationProcess`

**Agregar campo**:

```python
class MigrationProcess(models.Model):
    # ... campos existentes ...
    
    # 🆕 NUEVO: Campo para persistir configuración de tipos inferidos/definidos
    type_configuration = models.JSONField(
        null=True,
        blank=True,
        help_text="Configuración de tipos SQL por hoja y columna. "
                  "Formato: {sheet_name: {column: {sql_type, nullable, default_value}}}"
    )
    
    # 🆕 NUEVO: Timestamp de última inferencia de tipos
    types_inferred_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Fecha y hora de la última inferencia automática de tipos"
    )
```

### 4.2 Modificar Método `_save_dataframe_to_destination`

**Ubicación**: Dentro de `MigrationProcess`

**Cambios** (buscar y reemplazar):

```python
def _save_dataframe_to_destination(self, df, sheet_name, connection_dict, table_name):
    """
    Guarda un DataFrame en la base de datos destino.
    
    MEJORAS IMPLEMENTADAS:
    - Normalización de valores según tipo SQL
    - Validación de mappings antes de procesar
    - Mejor logging de errores
    - Manejo de valores mixtos
    """
    from .sql_utils import get_sql_server_connection
    from .utils.validators import normalize_dataframe_by_mappings, validate_column_mappings
    
    try:
        # 1. Obtener configuración de columnas para esta hoja
        column_mappings_dict = self.column_mappings or {}
        sheet_mappings = column_mappings_dict.get(sheet_name, {})
        
        if not sheet_mappings:
            logger.warning(f"No hay mappings de columnas para hoja '{sheet_name}'")
            return
        
        # 2. Validar mappings
        is_valid, errors = validate_column_mappings(df, sheet_mappings)
        if not is_valid:
            error_messages = [e['message'] for e in errors]
            raise ValueError(f"Errores en configuración de columnas: {'; '.join(error_messages)}")
        
        # 3. Normalizar DataFrame según tipos configurados
        logger.info(f"Normalizando datos de hoja '{sheet_name}'...")
        df_normalized, warnings = normalize_dataframe_by_mappings(df, sheet_mappings)
        
        # Log de advertencias
        for warning in warnings:
            logger.warning(f"Columna '{warning['column']}': {warning['message']}")
        
        # 4. Filtrar solo columnas seleccionadas
        selected_columns = list(sheet_mappings.keys())
        df_filtered = df_normalized[selected_columns].copy()
        
        # 5. Renombrar columnas según configuración
        rename_dict = {
            original: config.get('renamed_to', original)
            for original, config in sheet_mappings.items()
        }
        df_filtered.rename(columns=rename_dict, inplace=True)
        
        # 6. Convertir DataFrame a registros
        records = df_filtered.values.tolist()
        columns = list(df_filtered.columns)
        
        logger.info(f"Preparados {len(records)} registros con {len(columns)} columnas")
        
        # 7. Construir query de inserción
        placeholders = ', '.join(['?' for _ in columns])
        columns_str = ', '.join([f'[{col}]' for col in columns])
        insert_query = f"INSERT INTO {table_name} ({columns_str}) VALUES ({placeholders})"
        
        # 8. Conectar y ejecutar
        conn = get_sql_server_connection(connection_dict)
        cursor = conn.cursor()
        
        # Insertar en lotes para mejor rendimiento
        batch_size = 1000
        total_inserted = 0
        
        for i in range(0, len(records), batch_size):
            batch = records[i:i + batch_size]
            cursor.executemany(insert_query, batch)
            conn.commit()
            total_inserted += len(batch)
            logger.info(f"Insertados {total_inserted}/{len(records)} registros")
        
        cursor.close()
        conn.close()
        
        logger.info(f"✅ Hoja '{sheet_name}' procesada exitosamente: {total_inserted} registros")
        
    except Exception as e:
        logger.error(f"❌ Error al guardar hoja '{sheet_name}': {e}", exc_info=True)
        logger.error(f"SQL Query: {insert_query if 'insert_query' in locals() else 'N/A'}")
        logger.error(f"Columnas problemáticas: {columns if 'columns' in locals() else 'N/A'}")
        raise
```

---

## 🎨 PASO 5: MODIFICAR TEMPLATE HTML

### 5.1 Estructura del Renombrado de Hoja Activa

**Archivo**: `automatizacion/templates/automatizacion/excel_multi_sheet_selector.html`

**Buscar la sección de tabs de hojas y agregar input de renombrado SOLO en la hoja activa:**

```html
<!-- Sección de tabs de hojas -->
<div class="sheet-tabs">
    {% for sheet_name in sheet_names %}
    <div class="sheet-tab {% if forloop.first %}active{% endif %}" 
         data-sheet="{{ sheet_name }}" 
         onclick="switchSheet('{{ sheet_name }}')">
        <span class="sheet-name">{{ sheet_name }}</span>
        <span class="badge bg-primary" 
              id="badge-{{ sheet_name|slugify }}" 
              style="display: none;">0</span>
    </div>
    {% endfor %}
</div>

<!-- 🆕 NUEVO: Input de renombrado SOLO para hoja activa -->
<div class="card mt-3" id="active-sheet-rename-section">
    <div class="card-body">
        <h6 class="card-title">
            <i class="bi bi-pencil-square"></i>
            Renombrar Hoja Activa
        </h6>
        <div class="input-group">
            <span class="input-group-text">Nombre de tabla:</span>
            <input type="text" 
                   class="form-control" 
                   id="active-sheet-rename-input"
                   placeholder="ventas_2024"
                   data-original-name="">
            <button class="btn btn-outline-secondary" 
                    type="button" 
                    id="validate-rename-btn">
                <i class="bi bi-check-circle"></i> Validar
            </button>
        </div>
        <div class="invalid-feedback" id="rename-error" style="display: none;"></div>
        <div class="valid-feedback" id="rename-success" style="display: none;"></div>
        <small class="text-muted">
            ℹ️ Se normalizará automáticamente: minúsculas, guiones bajos, sin caracteres especiales
        </small>
    </div>
</div>
```

### 5.2 Mover Botón "Seleccionar Todas"

**Buscar**:

```html
<!-- Columnas disponibles -->
<div class="mb-3">
    <h5>Columnas disponibles</h5>
    <!-- 🆕 MOVER EL BOTÓN AQUÍ (DEBAJO del título) -->
    <button class="btn btn-sm btn-outline-primary mb-2" 
            onclick="selectAllColumns(currentSheet)">
        <i class="bi bi-check-all"></i> Seleccionar todas
    </button>
    
    <div id="columns-list-{{ sheet_name|slugify }}">
        <!-- checkboxes de columnas -->
    </div>
</div>
```

### 5.3 Corregir Checkboxes y Valores por Defecto

**Buscar el código de generación de checkboxes y reemplazar**:

```html
<!-- Por cada columna -->
<div class="form-check column-item">
    <input class="form-check-input column-selector" 
           type="checkbox" 
           id="col-{{ sheet_name|slugify }}-{{ forloop.counter }}"
           data-sheet="{{ sheet_name }}"
           data-column="{{ column }}"
           onchange="updateColumnSelection('{{ sheet_name }}')">
    <label class="form-check-label" for="col-{{ sheet_name|slugify }}-{{ forloop.counter }}">
        {{ column }}
    </label>
    
    <!-- 🆕 Configuración expandible (se muestra AL SELECCIONAR) -->
    <div class="column-config" 
         id="config-{{ sheet_name|slugify }}-{{ forloop.counter }}" 
         style="display: none; margin-top: 10px; padding-left: 25px;">
        
        <!-- Renombrar columna -->
        <div class="mb-2">
            <label class="form-label small">Renombrar a:</label>
            <input type="text" 
                   class="form-control form-control-sm column-rename-input"
                   data-sheet="{{ sheet_name }}"
                   data-original-name="{{ column }}"
                   placeholder="{{ column }}"
                   disabled>
        </div>
        
        <!-- Tipo SQL con inferencia -->
        <div class="mb-2">
            <label class="form-label small">Tipo SQL:</label>
            <select class="form-select form-select-sm column-type-selector"
                    data-sheet="{{ sheet_name }}"
                    data-column="{{ column }}"
                    onchange="onSqlTypeChange('{{ sheet_name }}', '{{ column }}', {{ forloop.counter }}, '{{ sheet_name|slugify }}')"
                    disabled>
                <option value="INT">INT</option>
                <option value="BIGINT">BIGINT</option>
                <option value="SMALLINT">SMALLINT</option>
                <option value="FLOAT">FLOAT</option>
                <option value="DECIMAL(18,2)">DECIMAL(18,2)</option>
                <option value="NVARCHAR(255)" selected>NVARCHAR(255)</option>
                <option value="NVARCHAR(100)">NVARCHAR(100)</option>
                <option value="NVARCHAR(50)">NVARCHAR(50)</option>
                <option value="DATE">DATE</option>
                <option value="DATETIME2">DATETIME2</option>
                <option value="BIT">BIT</option>
                <option value="TEXT">TEXT</option>
            </select>
            <small class="text-muted inferred-type-hint" id="hint-{{ sheet_name|slugify }}-{{ forloop.counter }}"></small>
        </div>
        
        <!-- Checkbox Nullable -->
        <div class="form-check mb-2">
            <input class="form-check-input column-nullable-checkbox" 
                   type="checkbox" 
                   id="nullable-{{ sheet_name|slugify }}-{{ forloop.counter }}"
                   data-sheet="{{ sheet_name }}"
                   data-column="{{ column }}"
                   onchange="toggleDefaultInput('{{ sheet_name }}', '{{ column }}', {{ forloop.counter }}, '{{ sheet_name|slugify }}')"
                   checked
                   disabled>
            <label class="form-check-label small" for="nullable-{{ sheet_name|slugify }}-{{ forloop.counter }}">
                Puede ser NULL
            </label>
        </div>
        
        <!-- Input Valor por Defecto -->
        <div class="mb-2">
            <label class="form-label small">Valor por defecto:</label>
            <input type="text" 
                   class="form-control form-control-sm column-default-input"
                   id="default-{{ sheet_name|slugify }}-{{ forloop.counter }}"
                   data-sheet="{{ sheet_name }}"
                   data-column="{{ column }}"
                   data-sql-type="NVARCHAR(255)"
                   placeholder="Ej: 0, '', GETDATE()"
                   disabled>
        </div>
    </div>
</div>
```

### 5.4 JavaScript: Función para Actualizar Selección

**Buscar `updateColumnSelection` y reemplazar**:

```javascript
function updateColumnSelection(sheetName) {
    const checkboxes = document.querySelectorAll(`input.column-selector[data-sheet="${sheetName}"]`);
    const selected = [];
    
    checkboxes.forEach((checkbox) => {
        const isChecked = checkbox.checked;
        const columnName = checkbox.dataset.column;
        const checkboxId = checkbox.id;
        const counter = checkboxId.split('-').pop();
        const sheetSlug = sheetName.replace(/[^a-zA-Z0-9]/g, '-').toLowerCase();
        
        // Encontrar elementos de configuración
        const configRow = document.getElementById(`config-${sheetSlug}-${counter}`);
        const renameInput = document.querySelector(`input.column-rename-input[data-sheet="${sheetName}"][data-original-name="${columnName}"]`);
        const typeSelector = document.querySelector(`select.column-type-selector[data-sheet="${sheetName}"][data-column="${columnName}"]`);
        const nullableCheckbox = document.getElementById(`nullable-${sheetSlug}-${counter}`);
        const defaultInput = document.getElementById(`default-${sheetSlug}-${counter}`);
        
        if (isChecked) {
            selected.push(columnName);
            
            // 🔧 FIX: Mostrar configuración y HABILITAR todos los campos inmediatamente
            if (configRow) {
                configRow.style.display = 'block';
            }
            
            if (renameInput) {
                renameInput.disabled = false;
            }
            
            if (typeSelector) {
                typeSelector.disabled = false;
                // Inferir tipo automáticamente
                inferTypeForColumn(sheetName, columnName, counter, sheetSlug);
            }
            
            if (nullableCheckbox) {
                nullableCheckbox.disabled = false;
            }
            
            // 🔧 FIX CRÍTICO: Activar input de default si nullable está desmarcado
            if (defaultInput) {
                const isNullable = nullableCheckbox ? nullableCheckbox.checked : true;
                defaultInput.disabled = isNullable;  // Habilitado si NO es nullable
            }
            
        } else {
            // Ocultar y deshabilitar si se desmarca
            if (configRow) {
                configRow.style.display = 'none';
            }
            
            if (renameInput) renameInput.disabled = true;
            if (typeSelector) typeSelector.disabled = true;
            if (nullableCheckbox) nullableCheckbox.disabled = true;
            if (defaultInput) defaultInput.disabled = true;
        }
    });
    
    // Actualizar lista de seleccionados
    selectedColumns[sheetName] = selected;
    
    // Actualizar UI
    updateSheetBadge(sheetName, selected.length);
}
```

### 5.5 JavaScript: Función para Inferir Tipos

**Agregar nueva función**:

```javascript
/**
 * Infiere el tipo SQL de una columna usando AJAX
 */
function inferTypeForColumn(sheetName, columnName, counter, sheetSlug) {
    const sourceId = document.getElementById('sourceId').value;
    const hintElement = document.getElementById(`hint-${sheetSlug}-${counter}`);
    const typeSelector = document.querySelector(`select.column-type-selector[data-sheet="${sheetName}"][data-column="${columnName}"]`);
    
    if (!typeSelector) return;
    
    // Mostrar loading
    if (hintElement) {
        hintElement.textContent = '⏳ Analizando...';
    }
    
    // Llamar endpoint de inferencia
    fetch(`/automatizacion/excel/${sourceId}/infer-types/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify({
            sheet_name: sheetName,
            columns: [columnName]
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.types && data.types[columnName]) {
            const typeInfo = data.types[columnName];
            
            // Seleccionar tipo inferido
            typeSelector.value = typeInfo.sql_type;
            
            // Mostrar hint con confianza
            if (hintElement) {
                const confidence = (typeInfo.confidence * 100).toFixed(0);
                hintElement.textContent = `💡 Sugerido: ${typeInfo.sql_type} (${confidence}% confianza)`;
                
                if (typeInfo.warnings && typeInfo.warnings.length > 0) {
                    hintElement.textContent += ` ⚠️ ${typeInfo.warnings[0]}`;
                }
            }
            
            // Configurar nullable y default
            const nullableCheckbox = document.getElementById(`nullable-${sheetSlug}-${counter}`);
            if (nullableCheckbox) {
                nullableCheckbox.checked = typeInfo.nullable;
            }
            
            const defaultInput = document.getElementById(`default-${sheetSlug}-${counter}`);
            if (defaultInput && typeInfo.default_value) {
                defaultInput.placeholder = `Ej: ${typeInfo.default_value}`;
                defaultInput.dataset.sqlType = typeInfo.sql_type;
            }
        }
    })
    .catch(error => {
        console.error('Error al inferir tipo:', error);
        if (hintElement) {
            hintElement.textContent = '❌ Error al analizar';
        }
    });
}

/**
 * Obtener cookie CSRF
 */
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
```

### 5.6 JavaScript: Validación de Renombrado en Tiempo Real

**Agregar**:

```javascript
// Evento para validar renombrado de hoja activa
document.getElementById('validate-rename-btn').addEventListener('click', function() {
    const input = document.getElementById('active-sheet-rename-input');
    const newName = input.value.trim();
    const originalName = input.dataset.originalName;
    const errorDiv = document.getElementById('rename-error');
    const successDiv = document.getElementById('rename-success');
    
    if (!newName) {
        input.classList.add('is-invalid');
        errorDiv.textContent = 'El nombre no puede estar vacío';
        errorDiv.style.display = 'block';
        successDiv.style.display = 'none';
        return;
    }
    
    // Obtener nombres existentes (excepto el actual)
    const existingNames = Object.keys(sheetRenames).filter(n => n !== originalName);
    
    // Llamar endpoint de validación
    fetch('/automatizacion/validate-sheet-rename/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify({
            original_name: originalName,
            new_name: newName,
            existing_names: existingNames
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.valid) {
            input.classList.remove('is-invalid');
            input.classList.add('is-valid');
            input.value = data.normalized;
            errorDiv.style.display = 'none';
            successDiv.textContent = `✓ Nombre válido: ${data.normalized}`;
            successDiv.style.display = 'block';
            
            // Guardar en objeto de renombrados
            sheetRenames[originalName] = data.normalized;
        } else {
            input.classList.add('is-invalid');
            input.classList.remove('is-valid');
            errorDiv.textContent = data.error;
            errorDiv.style.display = 'block';
            successDiv.style.display = 'none';
        }
    })
    .catch(error => {
        console.error('Error al validar nombre:', error);
        input.classList.add('is-invalid');
        errorDiv.textContent = 'Error al validar el nombre';
        errorDiv.style.display = 'block';
    });
});

// Actualizar input de renombrado al cambiar de hoja
function switchSheet(sheetName) {
    // ... código existente ...
    
    // Actualizar input de renombrado
    const renameInput = document.getElementById('active-sheet-rename-input');
    if (renameInput) {
        renameInput.dataset.originalName = sheetName;
        renameInput.value = sheetRenames[sheetName] || '';
        renameInput.placeholder = `Renombrar "${sheetName}"`;
        renameInput.classList.remove('is-valid', 'is-invalid');
        document.getElementById('rename-error').style.display = 'none';
        document.getElementById('rename-success').style.display = 'none';
    }
}
```

---

## 🧪 PASO 6: CREAR TESTS

**Archivo**: `automatizacion/tests/test_validation_system.py`

```python
"""
Tests del sistema de validación y normalización.
"""

import pytest
import pandas as pd
from automatizacion.utils.validators import (
    normalize_name,
    validate_sheet_name,
    infer_sql_type,
    normalize_value_by_type,
    normalize_dataframe_by_mappings
)


class TestNormalizeName:
    """Tests para normalize_name"""
    
    def test_basic_normalization(self):
        """Normalización básica: espacios → guiones bajos"""
        assert normalize_name("Hoja 1") == "hoja_1"
        assert normalize_name("Datos Ventas") == "datos_ventas"
    
    def test_special_characters(self):
        """Eliminar caracteres especiales"""
        assert normalize_name("Datos-Ventas!") == "datos_ventas"
        assert normalize_name("Hoja#1@2024") == "hoja_1_2024"
    
    def test_starts_with_number(self):
        """No puede empezar con número"""
        assert normalize_name("123tabla") == "tabla_123"
        assert normalize_name("2024_ventas") == "tabla_2024_ventas"
    
    def test_avoid_duplicates(self):
        """Evitar duplicados con sufijo incremental"""
        existing = ["hoja", "hoja_1"]
        assert normalize_name("Hoja", existing) == "hoja_2"
    
    def test_empty_name(self):
        """Nombre vacío → 'sin_nombre'"""
        assert normalize_name("") == "sin_nombre"
        assert normalize_name("   ") == "sin_nombre"


class TestInferSqlType:
    """Tests para inferencia de tipos SQL"""
    
    def test_integer_type(self):
        """Detectar INT"""
        s = pd.Series([1, 2, 3, 4, 5])
        result = infer_sql_type(s)
        assert result['sql_type'] == 'TINYINT'  # 0-255
        assert result['confidence'] == 1.0
        assert result['default_value'] == '0'
    
    def test_float_type(self):
        """Detectar FLOAT"""
        s = pd.Series([1.5, 2.3, 3.7])
        result = infer_sql_type(s)
        assert result['sql_type'] == 'FLOAT'
        assert result['confidence'] == 1.0
    
    def test_boolean_type(self):
        """Detectar BIT (booleano)"""
        s = pd.Series(['true', 'false', '1', '0'])
        result = infer_sql_type(s)
        assert result['sql_type'] == 'BIT'
    
    def test_date_type(self):
        """Detectar DATE"""
        s = pd.Series(['2024-01-15', '2024-02-20', '2024-03-30'])
        result = infer_sql_type(s)
        assert 'DATE' in result['sql_type']
    
    def test_varchar_type(self):
        """Detectar VARCHAR con longitud apropiada"""
        s = pd.Series(['texto corto', 'otro texto'])
        result = infer_sql_type(s)
        assert 'NVARCHAR' in result['sql_type']
    
    def test_mixed_types_warning(self):
        """Detectar tipos mixtos"""
        s = pd.Series([1, 2, 'abc', 4, 5])
        result = infer_sql_type(s)
        assert result['mixed_types'] == True
        assert len(result['warnings']) > 0
    
    def test_nullable_detection(self):
        """Detectar si debe ser nullable"""
        s_with_nulls = pd.Series([1, 2, None, 4, None, None])
        result = infer_sql_type(s_with_nulls)
        assert result['nullable'] == True  # >5% nulos


class TestNormalizeValueByType:
    """Tests para normalización de valores"""
    
    def test_int_empty_not_nullable(self):
        """INT vacío + NO nullable → 0"""
        assert normalize_value_by_type(None, 'INT', nullable=False) == 0
        assert normalize_value_by_type('', 'INT', nullable=False) == 0
    
    def test_int_empty_nullable(self):
        """INT vacío + nullable → NULL"""
        assert normalize_value_by_type(None, 'INT', nullable=True) is None
    
    def test_int_valid_conversion(self):
        """INT con string numérico"""
        assert normalize_value_by_type('123', 'INT') == 123
        assert normalize_value_by_type('45.7', 'INT') == 45  # Trunca
    
    def test_float_requires_decimal(self):
        """FLOAT acepta enteros y decimales"""
        assert normalize_value_by_type('12.5', 'FLOAT') == 12.5
        assert normalize_value_by_type('88', 'FLOAT') == 88.0
    
    def test_varchar_empty_not_nullable(self):
        """VARCHAR vacío + NO nullable → ''"""
        assert normalize_value_by_type(None, 'VARCHAR(50)', nullable=False) == ''
        assert normalize_value_by_type('', 'VARCHAR(50)', nullable=False) == ''
    
    def test_varchar_truncation(self):
        """VARCHAR trunca si excede longitud"""
        long_text = 'a' * 100
        result = normalize_value_by_type(long_text, 'VARCHAR(50)', nullable=False)
        assert len(result) == 50
    
    def test_date_getdate(self):
        """DATE acepta GETDATE()"""
        assert normalize_value_by_type('GETDATE()', 'DATE') == 'GETDATE()'
    
    def test_date_string_conversion(self):
        """DATE convierte string a formato SQL"""
        result = normalize_value_by_type('2024-01-15', 'DATE')
        assert '2024-01-15' in result
    
    def test_bit_true_values(self):
        """BIT mapea valores truthy"""
        assert normalize_value_by_type('true', 'BIT') == 1
        assert normalize_value_by_type('yes', 'BIT') == 1
        assert normalize_value_by_type('1', 'BIT') == 1
        assert normalize_value_by_type('sí', 'BIT') == 1
    
    def test_bit_false_values(self):
        """BIT mapea valores falsy"""
        assert normalize_value_by_type('false', 'BIT') == 0
        assert normalize_value_by_type('no', 'BIT') == 0
        assert normalize_value_by_type('0', 'BIT') == 0


class TestNormalizeDataFrameByMappings:
    """Tests para normalización de DataFrame completo"""
    
    def test_basic_normalization(self):
        """Normalización básica de DataFrame"""
        df = pd.DataFrame({
            'edad': ['25', None, '30'],
            'activo': ['true', 'false', '1']
        })
        
        mappings = {
            'edad': {
                'renamed_to': 'edad',
                'sql_type': 'INT',
                'nullable': False,
                'default_value': '0'
            },
            'activo': {
                'renamed_to': 'activo',
                'sql_type': 'BIT',
                'nullable': False,
                'default_value': '0'
            }
        }
        
        result_df, warnings = normalize_dataframe_by_mappings(df, mappings)
        
        # Verificar edad
        assert result_df['edad'].tolist() == [25, 0, 30]
        
        # Verificar activo
        assert result_df['activo'].tolist() == [1, 0, 1]
    
    def test_mixed_type_handling(self):
        """Manejo de tipos mixtos con advertencias"""
        df = pd.DataFrame({
            'cantidad': ['10', '20', 'abc', '30']
        })
        
        mappings = {
            'cantidad': {
                'renamed_to': 'cantidad',
                'sql_type': 'INT',
                'nullable': False,
                'default_value': '0'
            }
        }
        
        result_df, warnings = normalize_dataframe_by_mappings(df, mappings)
        
        # 'abc' no se puede convertir → default (0)
        assert result_df['cantidad'].tolist() == [10, 20, 0, 30]


# Fixtures para tests
@pytest.fixture
def sample_dataframe():
    """DataFrame de ejemplo para tests"""
    return pd.DataFrame({
        'id': [1, 2, 3, 4, 5],
        'nombre': ['Juan', 'María', 'Pedro', None, 'Ana'],
        'edad': [25, 30, None, 35, 28],
        'salario': [1500.50, 2000.00, None, 2500.75, 1800.00],
        'activo': ['true', 'false', '1', '0', 'yes'],
        'fecha_ingreso': ['2024-01-15', '2024-02-20', None, '2024-03-30', '2024-04-10']
    })


@pytest.fixture
def sample_column_mappings():
    """Mappings de ejemplo para tests"""
    return {
        'id': {
            'renamed_to': 'id',
            'sql_type': 'INT',
            'nullable': False,
            'default_value': '0'
        },
        'nombre': {
            'renamed_to': 'nombre',
            'sql_type': 'NVARCHAR(100)',
            'nullable': True,
            'default_value': None
        },
        'edad': {
            'renamed_to': 'edad',
            'sql_type': 'INT',
            'nullable': True,
            'default_value': None
        },
        'salario': {
            'renamed_to': 'salario',
            'sql_type': 'FLOAT',
            'nullable': True,
            'default_value': None
        },
        'activo': {
            'renamed_to': 'activo',
            'sql_type': 'BIT',
            'nullable': False,
            'default_value': '0'
        },
        'fecha_ingreso': {
            'renamed_to': 'fecha_ingreso',
            'sql_type': 'DATE',
            'nullable': True,
            'default_value': None
        }
    }
```

---

## 🔧 PASO 7: EJECUTAR MIGRACIONES

```bash
# 1. Crear migraciones para el nuevo campo type_configuration
python manage.py makemigrations

# 2. Aplicar migraciones
python manage.py migrate
```

---

## ✅ CHECKLIST DE PRUEBAS

Voy a crear un archivo separado con el checklist completo...
