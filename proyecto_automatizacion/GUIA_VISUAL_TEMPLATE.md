# 🎨 GUÍA VISUAL - CAMBIOS EN EXCEL_MULTI_SHEET_SELECTOR.HTML

## 📐 LAYOUT ACTUAL vs NUEVO

### ANTES (Problemático)

```
┌─────────────────────────────────────────────────┐
│ [Hoja1] [Hoja2] [Hoja3]  <-- Tabs              │
├─────────────────────────────────────────────────┤
│                                                 │
│ Columnas disponibles                            │
│                                                 │
│ ☐ columna1                                      │
│ ☐ columna2                                      │
│ ☐ columna3                                      │
│                                                 │
│ [Seleccionar todas] <-- ❌ PROBLEMA: ARRIBA    │
│                                                 │
│ Columnas seleccionadas: 0                       │
└─────────────────────────────────────────────────┘

PROBLEMAS:
❌ Vista intermedia /sheets/ antes de llegar aquí
❌ Botón "Seleccionar todas" arriba (debe estar abajo)
❌ No se puede renombrar hoja activa
❌ Checkbox nullable y input default desactivados al inicio
```

---

### DESPUÉS (Corregido)

```
┌─────────────────────────────────────────────────────────────┐
│ [Hoja1*] [Hoja2] [Hoja3]  <-- Tabs (* = activa)            │
├─────────────────────────────────────────────────────────────┤
│ 🆕 Renombrar Hoja Activa                                    │
│ ┌─────────────────────────────────────────────────────┐     │
│ │ Nombre de tabla: [ventas_2024___________] [Validar]│     │
│ │ ℹ️ Se normalizará: minúsculas, guiones bajos         │     │
│ └─────────────────────────────────────────────────────┘     │
├─────────────────────────────────────────────────────────────┤
│ Columnas disponibles                                        │
│                                                             │
│ 🆕 [Seleccionar todas] <-- ✅ MOVIDO AQUÍ (DEBAJO)        │
│                                                             │
│ ☐ edad                                                      │
│ ☐ nombre                                                    │
│ ☑ salario  <-- SELECCIONADO                                │
│   │                                                         │
│   └─> 🆕 CONFIGURACIÓN EXPANDIBLE (se muestra al marcar):  │
│       ┌───────────────────────────────────────────────┐    │
│       │ Renombrar a: [salario___________] ✅ Habilitado│    │
│       │ Tipo SQL: [FLOAT ▼] ✅ Habilitado              │    │
│       │   💡 Sugerido: FLOAT (100% confianza)         │    │
│       │                                                │    │
│       │ ☑ Puede ser NULL ✅ Habilitado                 │    │
│       │                                                │    │
│       │ Valor por defecto: [0.0_____] ⚙️ Habilitado   │    │
│       │   (placeholder dinámico según tipo SQL)       │    │
│       └───────────────────────────────────────────────┘    │
│                                                             │
│ Columnas seleccionadas: 1                                   │
└─────────────────────────────────────────────────────────────┘

MEJORAS:
✅ Sin vista /sheets/ intermedia (redirect directo)
✅ Renombrado de hoja activa con validación en tiempo real
✅ Botón "Seleccionar todas" debajo de "Columnas disponibles"
✅ Configuración por campo (no global)
✅ Todos los campos habilitados al seleccionar
✅ Input default habilitado correctamente según nullable
✅ Inferencia automática con hints
✅ Placeholder dinámico
```

---

## 🔧 CÓDIGO HTML - SECCIÓN POR SECCIÓN

### 1️⃣ Sección: Renombrado de Hoja Activa

**Agregar DESPUÉS de los tabs de hojas**:

```html
<!-- NUEVO: Renombrado de hoja activa -->
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
                   data-original-name=""
                   autocomplete="off">
            <button class="btn btn-outline-secondary" 
                    type="button" 
                    id="validate-rename-btn">
                <i class="bi bi-check-circle"></i> Validar
            </button>
        </div>
        
        <!-- Feedback de validación -->
        <div class="invalid-feedback d-none" id="rename-error"></div>
        <div class="valid-feedback d-none" id="rename-success"></div>
        
        <small class="text-muted d-block mt-2">
            <i class="bi bi-info-circle"></i>
            Se normalizará automáticamente: minúsculas, guiones bajos, sin caracteres especiales
        </small>
    </div>
</div>
```

**CSS asociado**:
```css
#active-sheet-rename-section {
    border-left: 4px solid #0d6efd;
}

#active-sheet-rename-input.is-valid {
    border-color: #198754;
    padding-right: calc(1.5em + 0.75rem);
    background-image: url("data:image/svg+xml,..."); /* checkmark */
}

#active-sheet-rename-input.is-invalid {
    border-color: #dc3545;
}

.invalid-feedback, .valid-feedback {
    display: none;
}

.invalid-feedback.d-block, .valid-feedback.d-block {
    display: block !important;
}
```

---

### 2️⃣ Sección: Botón "Seleccionar Todas"

**ANTES** (ubicación incorrecta):
```html
<!-- ❌ NO HACER ESTO -->
<h5>Columnas disponibles</h5>

<div id="columns-list">
    <!-- checkboxes -->
</div>

<button onclick="selectAllColumns()">Seleccionar todas</button>
```

**DESPUÉS** (ubicación correcta):
```html
<!-- ✅ HACER ESTO -->
<h5>Columnas disponibles</h5>

<!-- Botón DEBAJO del título, ANTES de la lista -->
<button class="btn btn-sm btn-outline-primary mb-3" 
        id="select-all-btn-{{ sheet_name|slugify }}"
        onclick="selectAllColumns('{{ sheet_name }}')">
    <i class="bi bi-check-all"></i> Seleccionar todas
</button>

<div id="columns-list-{{ sheet_name|slugify }}">
    <!-- checkboxes -->
</div>
```

---

### 3️⃣ Sección: Checkbox de Columna con Configuración Expandible

**REEMPLAZAR** el código de cada columna:

```html
{% for column in columns %}
<div class="column-item mb-2" id="item-{{ sheet_name|slugify }}-{{ forloop.counter }}">
    
    <!-- Checkbox principal -->
    <div class="form-check">
        <input class="form-check-input column-selector" 
               type="checkbox" 
               id="col-{{ sheet_name|slugify }}-{{ forloop.counter }}"
               data-sheet="{{ sheet_name }}"
               data-column="{{ column }}"
               onchange="updateColumnSelection('{{ sheet_name }}', '{{ column }}', {{ forloop.counter }})">
        
        <label class="form-check-label fw-semibold" 
               for="col-{{ sheet_name|slugify }}-{{ forloop.counter }}">
            {{ column }}
        </label>
    </div>
    
    <!-- 🆕 Configuración expandible (oculta por defecto) -->
    <div class="column-config mt-2 ms-4 p-3 border rounded bg-light" 
         id="config-{{ sheet_name|slugify }}-{{ forloop.counter }}" 
         style="display: none;">
        
        <!-- Renombrar columna -->
        <div class="mb-3">
            <label class="form-label small text-muted">
                <i class="bi bi-pencil"></i> Renombrar a:
            </label>
            <input type="text" 
                   class="form-control form-control-sm column-rename-input"
                   id="rename-{{ sheet_name|slugify }}-{{ forloop.counter }}"
                   data-sheet="{{ sheet_name }}"
                   data-original-name="{{ column }}"
                   placeholder="{{ column }}"
                   disabled>
        </div>
        
        <!-- Tipo SQL con inferencia -->
        <div class="mb-3">
            <label class="form-label small text-muted">
                <i class="bi bi-database"></i> Tipo SQL:
            </label>
            <select class="form-select form-select-sm column-type-selector"
                    id="type-{{ sheet_name|slugify }}-{{ forloop.counter }}"
                    data-sheet="{{ sheet_name }}"
                    data-column="{{ column }}"
                    onchange="onSqlTypeChange('{{ sheet_name }}', '{{ column }}', {{ forloop.counter }})"
                    disabled>
                <optgroup label="Números">
                    <option value="TINYINT">TINYINT (0-255)</option>
                    <option value="SMALLINT">SMALLINT (±32K)</option>
                    <option value="INT">INT (±2B)</option>
                    <option value="BIGINT">BIGINT (±9E18)</option>
                    <option value="FLOAT">FLOAT (decimal)</option>
                    <option value="DECIMAL(18,2)">DECIMAL(18,2)</option>
                </optgroup>
                <optgroup label="Texto">
                    <option value="NVARCHAR(50)">NVARCHAR(50)</option>
                    <option value="NVARCHAR(100)">NVARCHAR(100)</option>
                    <option value="NVARCHAR(255)" selected>NVARCHAR(255)</option>
                    <option value="NVARCHAR(MAX)">NVARCHAR(MAX)</option>
                    <option value="TEXT">TEXT</option>
                </optgroup>
                <optgroup label="Fechas">
                    <option value="DATE">DATE</option>
                    <option value="DATETIME2">DATETIME2</option>
                </optgroup>
                <optgroup label="Otros">
                    <option value="BIT">BIT (booleano)</option>
                </optgroup>
            </select>
            
            <!-- Hint de inferencia -->
            <small class="text-success d-block mt-1" 
                   id="hint-{{ sheet_name|slugify }}-{{ forloop.counter }}">
                <!-- Se llena dinámicamente: "💡 Sugerido: INT (95% confianza)" -->
            </small>
        </div>
        
        <!-- Checkbox Nullable -->
        <div class="form-check mb-3">
            <input class="form-check-input column-nullable-checkbox" 
                   type="checkbox" 
                   id="nullable-{{ sheet_name|slugify }}-{{ forloop.counter }}"
                   data-sheet="{{ sheet_name }}"
                   data-column="{{ column }}"
                   onchange="toggleDefaultInput('{{ sheet_name }}', '{{ column }}', {{ forloop.counter }})"
                   checked
                   disabled>
            <label class="form-check-label small" 
                   for="nullable-{{ sheet_name|slugify }}-{{ forloop.counter }}">
                Puede ser NULL
            </label>
        </div>
        
        <!-- Input Valor por Defecto -->
        <div class="mb-0">
            <label class="form-label small text-muted">
                <i class="bi bi-123"></i> Valor por defecto:
            </label>
            <input type="text" 
                   class="form-control form-control-sm column-default-input"
                   id="default-{{ sheet_name|slugify }}-{{ forloop.counter }}"
                   data-sheet="{{ sheet_name }}"
                   data-column="{{ column }}"
                   data-sql-type="NVARCHAR(255)"
                   placeholder="Ej: 0, '', GETDATE()"
                   disabled>
            
            <small class="text-muted d-block mt-1">
                <i class="bi bi-lightbulb"></i>
                Se aplica solo si el campo está vacío en el Excel
            </small>
        </div>
        
    </div><!-- fin column-config -->
    
</div><!-- fin column-item -->
{% endfor %}
```

---

## 🎨 CSS ADICIONAL

Agregar al final del archivo o en un `<style>` block:

```css
/* Estilo de column-item */
.column-item {
    transition: background-color 0.2s ease;
    padding: 8px;
    border-radius: 4px;
}

.column-item:hover {
    background-color: #f8f9fa;
}

/* Configuración expandible */
.column-config {
    animation: slideDown 0.3s ease-out;
    border-left: 3px solid #0d6efd;
}

@keyframes slideDown {
    from {
        opacity: 0;
        max-height: 0;
    }
    to {
        opacity: 1;
        max-height: 500px;
    }
}

/* Hints de inferencia */
.text-success {
    font-weight: 500;
}

/* Input de renombrado con validación */
.column-rename-input:focus {
    border-color: #86b7fe;
    box-shadow: 0 0 0 0.25rem rgba(13, 110, 253, 0.25);
}

/* Botón de seleccionar todas */
#select-all-btn {
    transition: all 0.2s ease;
}

#select-all-btn:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 8px rgba(0,0,0,0.1);
}

/* Badge de contador */
.sheet-tab .badge {
    font-size: 0.7rem;
    padding: 2px 6px;
    margin-left: 5px;
}
```

---

## 🎯 JAVASCRIPT - FUNCIONES PRINCIPALES

### Función 1: `updateColumnSelection()`

**Propósito**: Mostrar/ocultar configuración al marcar/desmarcar checkbox

```javascript
function updateColumnSelection(sheetName, columnName, counter) {
    const checkbox = document.getElementById(`col-${slugify(sheetName)}-${counter}`);
    const configDiv = document.getElementById(`config-${slugify(sheetName)}-${counter}`);
    const renameInput = document.getElementById(`rename-${slugify(sheetName)}-${counter}`);
    const typeSelector = document.getElementById(`type-${slugify(sheetName)}-${counter}`);
    const nullableCheckbox = document.getElementById(`nullable-${slugify(sheetName)}-${counter}`);
    const defaultInput = document.getElementById(`default-${slugify(sheetName)}-${counter}`);
    
    if (checkbox.checked) {
        // ✅ MOSTRAR y HABILITAR configuración
        configDiv.style.display = 'block';
        
        if (renameInput) renameInput.disabled = false;
        if (typeSelector) typeSelector.disabled = false;
        if (nullableCheckbox) nullableCheckbox.disabled = false;
        
        // 🔧 FIX CRÍTICO: Habilitar default si nullable=false
        if (defaultInput) {
            const isNullable = nullableCheckbox ? nullableCheckbox.checked : true;
            defaultInput.disabled = isNullable;
        }
        
        // Inferir tipo automáticamente
        inferTypeForColumn(sheetName, columnName, counter);
        
        // Actualizar contador
        selectedColumns[sheetName] = selectedColumns[sheetName] || [];
        if (!selectedColumns[sheetName].includes(columnName)) {
            selectedColumns[sheetName].push(columnName);
        }
        
    } else {
        // ❌ OCULTAR y DESHABILITAR configuración
        configDiv.style.display = 'none';
        
        if (renameInput) renameInput.disabled = true;
        if (typeSelector) typeSelector.disabled = true;
        if (nullableCheckbox) nullableCheckbox.disabled = true;
        if (defaultInput) defaultInput.disabled = true;
        
        // Remover de seleccionados
        if (selectedColumns[sheetName]) {
            selectedColumns[sheetName] = selectedColumns[sheetName].filter(c => c !== columnName);
        }
    }
    
    // Actualizar badge
    updateSheetBadge(sheetName, (selectedColumns[sheetName] || []).length);
}
```

---

### Función 2: `toggleDefaultInput()`

**Propósito**: Habilitar/deshabilitar input de default según nullable

```javascript
function toggleDefaultInput(sheetName, columnName, counter) {
    const nullableCheckbox = document.getElementById(`nullable-${slugify(sheetName)}-${counter}`);
    const defaultInput = document.getElementById(`default-${slugify(sheetName)}-${counter}`);
    
    if (!nullableCheckbox || !defaultInput) return;
    
    // 🔧 FIX: Habilitar input cuando nullable=FALSE
    const isNullable = nullableCheckbox.checked;
    defaultInput.disabled = isNullable;
    
    // Actualizar placeholder según tipo SQL
    const typeSelector = document.getElementById(`type-${slugify(sheetName)}-${counter}`);
    if (typeSelector && !isNullable) {
        updatePlaceholderForType(defaultInput, typeSelector.value);
    }
    
    // Limpiar valor si se marca nullable
    if (isNullable) {
        defaultInput.value = '';
    }
}
```

---

### Función 3: `inferTypeForColumn()`

**Propósito**: Llamar endpoint AJAX para inferir tipo SQL

```javascript
function inferTypeForColumn(sheetName, columnName, counter) {
    const sourceId = document.querySelector('[name="source_id"]').value;
    const hintElement = document.getElementById(`hint-${slugify(sheetName)}-${counter}`);
    const typeSelector = document.getElementById(`type-${slugify(sheetName)}-${counter}`);
    
    if (!typeSelector) return;
    
    // Mostrar loading
    if (hintElement) {
        hintElement.textContent = '⏳ Analizando...';
        hintElement.className = 'text-muted d-block mt-1';
    }
    
    // Llamar endpoint
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
                hintElement.className = 'text-success d-block mt-1';
                
                if (typeInfo.warnings && typeInfo.warnings.length > 0) {
                    hintElement.textContent += ` ⚠️ ${typeInfo.warnings[0]}`;
                    hintElement.className = 'text-warning d-block mt-1';
                }
            }
            
            // Configurar nullable
            const nullableCheckbox = document.getElementById(`nullable-${slugify(sheetName)}-${counter}`);
            if (nullableCheckbox) {
                nullableCheckbox.checked = typeInfo.nullable;
                toggleDefaultInput(sheetName, columnName, counter);
            }
            
            // Actualizar placeholder de default
            const defaultInput = document.getElementById(`default-${slugify(sheetName)}-${counter}`);
            if (defaultInput) {
                updatePlaceholderForType(defaultInput, typeInfo.sql_type);
            }
        }
    })
    .catch(error => {
        console.error('Error al inferir tipo:', error);
        if (hintElement) {
            hintElement.textContent = '❌ Error al analizar';
            hintElement.className = 'text-danger d-block mt-1';
        }
    });
}
```

---

### Función 4: `updatePlaceholderForType()`

**Propósito**: Cambiar placeholder dinámicamente según tipo SQL

```javascript
function updatePlaceholderForType(inputElement, sqlType) {
    const placeholders = {
        'TINYINT': 'Ej: 0',
        'SMALLINT': 'Ej: 0',
        'INT': 'Ej: 0',
        'BIGINT': 'Ej: 0',
        'FLOAT': 'Ej: 0.0',
        'DECIMAL': 'Ej: 0.00',
        'DATE': 'Ej: 2025-01-01 o GETDATE()',
        'DATETIME2': 'Ej: 2025-01-01 10:30:00 o GETDATE()',
        'BIT': 'Ej: 0 o 1',
        'NVARCHAR': "Ej: ''",
        'VARCHAR': "Ej: ''",
        'TEXT': "Ej: ''"
    };
    
    // Buscar coincidencia (ej: "DECIMAL(18,2)" contiene "DECIMAL")
    for (const [key, placeholder] of Object.entries(placeholders)) {
        if (sqlType.toUpperCase().includes(key)) {
            inputElement.placeholder = placeholder;
            inputElement.dataset.sqlType = sqlType;
            return;
        }
    }
    
    // Placeholder por defecto
    inputElement.placeholder = 'Ej: valor por defecto';
}
```

---

### Función 5: `onSqlTypeChange()`

**Propósito**: Actualizar placeholder al cambiar tipo SQL manualmente

```javascript
function onSqlTypeChange(sheetName, columnName, counter) {
    const typeSelector = document.getElementById(`type-${slugify(sheetName)}-${counter}`);
    const defaultInput = document.getElementById(`default-${slugify(sheetName)}-${counter}`);
    
    if (!typeSelector || !defaultInput) return;
    
    const selectedType = typeSelector.value;
    
    // Actualizar placeholder
    updatePlaceholderForType(defaultInput, selectedType);
    
    // Limpiar valor anterior (opcional)
    // defaultInput.value = '';
}
```

---

### Función 6: `validateSheetRename()`

**Propósito**: Validar renombrado de hoja en tiempo real

```javascript
document.getElementById('validate-rename-btn').addEventListener('click', function() {
    const input = document.getElementById('active-sheet-rename-input');
    const newName = input.value.trim();
    const originalName = input.dataset.originalName;
    const errorDiv = document.getElementById('rename-error');
    const successDiv = document.getElementById('rename-success');
    
    // Reset
    input.classList.remove('is-valid', 'is-invalid');
    errorDiv.classList.remove('d-block');
    successDiv.classList.remove('d-block');
    
    if (!newName) {
        input.classList.add('is-invalid');
        errorDiv.textContent = '❌ El nombre no puede estar vacío';
        errorDiv.classList.add('d-block');
        return;
    }
    
    // Obtener nombres existentes (excepto el actual)
    const existingNames = Object.keys(sheetRenames || {}).filter(n => n !== originalName);
    
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
            input.classList.add('is-valid');
            input.value = data.normalized;
            successDiv.textContent = `✓ Nombre válido: ${data.normalized}`;
            successDiv.classList.add('d-block');
            
            // Guardar en objeto de renombrados
            sheetRenames = sheetRenames || {};
            sheetRenames[originalName] = data.normalized;
            
        } else {
            input.classList.add('is-invalid');
            errorDiv.textContent = `❌ ${data.error}`;
            errorDiv.classList.add('d-block');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        input.classList.add('is-invalid');
        errorDiv.textContent = '❌ Error al validar el nombre';
        errorDiv.classList.add('d-block');
    });
});
```

---

### Función 7: `switchSheet()`

**Propósito**: Actualizar input de renombrado al cambiar de hoja

```javascript
function switchSheet(sheetName) {
    // ... código existente de cambio de tabs ...
    
    // Actualizar input de renombrado
    const renameInput = document.getElementById('active-sheet-rename-input');
    if (renameInput) {
        renameInput.dataset.originalName = sheetName;
        renameInput.value = sheetRenames[sheetName] || '';
        renameInput.placeholder = `Renombrar "${sheetName}"`;
        renameInput.classList.remove('is-valid', 'is-invalid');
        
        // Reset feedback
        document.getElementById('rename-error').classList.remove('d-block');
        document.getElementById('rename-success').classList.remove('d-block');
    }
    
    // ... resto del código ...
}
```

---

## 🚀 ORDEN DE IMPLEMENTACIÓN

### Paso 1: Estructura HTML
1. Agregar sección de renombrado de hoja activa
2. Mover botón "Seleccionar todas"
3. Refactorizar checkboxes con configuración expandible

### Paso 2: CSS
1. Agregar estilos de validación (is-valid, is-invalid)
2. Agregar animaciones de slideDown
3. Estilos de hover y focus

### Paso 3: JavaScript
1. Modificar `updateColumnSelection()` para habilitar campos
2. Agregar `toggleDefaultInput()` para fix del bug
3. Agregar `inferTypeForColumn()` para AJAX
4. Agregar `updatePlaceholderForType()` para placeholders dinámicos
5. Agregar evento de validación de renombrado
6. Modificar `switchSheet()` para actualizar input

---

## ✅ CHECKLIST DE VERIFICACIÓN

- [ ] Input de renombrado visible y funcional
- [ ] Botón "Validar" llama endpoint AJAX
- [ ] Normalización funciona (espacios → underscores)
- [ ] Detecta duplicados
- [ ] Botón "Seleccionar todas" debajo de título
- [ ] Al marcar checkbox, aparece configuración
- [ ] Todos los campos habilitados al seleccionar
- [ ] Input default HABILITADO cuando nullable=FALSE
- [ ] Input default DESHABILITADO cuando nullable=TRUE
- [ ] Inferencia automática funciona
- [ ] Hint muestra tipo sugerido + confianza
- [ ] Placeholder cambia según tipo SQL
- [ ] Al cambiar tipo manualmente, placeholder se actualiza
- [ ] Al cambiar de hoja, input de renombrado se actualiza

---

## 📊 EJEMPLO DE FLUJO COMPLETO

### Usuario abre `/automatizacion/excel/123/multi-config/`

1. **Se muestra**:
   - Tabs de hojas: [Hoja1*] [Hoja2] [Hoja3]
   - Input de renombrado: "Renombrar Hoja Activa"
   - Lista de columnas con checkboxes

2. **Usuario escribe** "Ventas 2024!" en input de renombrado
   - Clic en "Validar"
   - AJAX → `/validate-sheet-rename/`
   - Respuesta: `{valid: true, normalized: 'ventas_2024'}`
   - Input cambia a "ventas_2024", borde verde, ✓

3. **Usuario marca** checkbox de "edad"
   - Aparece configuración expandible (slideDown)
   - Campos habilitados: renombrar, tipo, nullable, default
   - AJAX → `/excel/123/infer-types/`
   - Respuesta: `{sql_type: 'INT', confidence: 1.0, nullable: false}`
   - Selector cambia a "INT"
   - Hint: "💡 Sugerido: INT (100% confianza)"
   - Checkbox nullable desmarcado
   - Input default HABILITADO (porque nullable=false)
   - Placeholder: "Ej: 0"

4. **Usuario desmarca** checkbox "Puede ser NULL"
   - Input default se HABILITA
   - Placeholder: "Ej: 0"

5. **Usuario cambia** tipo a "FLOAT"
   - Placeholder cambia a "Ej: 0.0"

6. **Usuario guarda** configuración
   - JSON enviado al backend:
   ```json
   {
     "Hoja1": {
       "renamed_to": "ventas_2024",
       "columns": {
         "edad": {
           "renamed_to": "edad",
           "sql_type": "FLOAT",
           "nullable": false,
           "default_value": "0.0"
         }
       }
     }
   }
   ```

---

**¡Implementación lista! 🚀**
