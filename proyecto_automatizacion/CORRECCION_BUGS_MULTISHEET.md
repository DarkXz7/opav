# 🐛 Análisis y Corrección de Bugs Críticos: Multi-Sheet Selector

## 📋 Problemas Identificados

### 🔴 **Problema 1: Duplicación de Columnas al "Seleccionar Todo"**

**Síntoma:** Al pulsar "Seleccionar todo", aparecen 21 columnas en vez de 7 reales.

**Causa Probable:**
El selector `input[data-sheet="${sheetName}"][data-column]` puede estar encontrando checkboxes duplicados en el DOM si:
1. Los checkboxes no tienen un `id` único
2. Hay múltiples elementos con el mismo `data-column` para la misma hoja
3. El template Django está generando duplicados en el loop

**Investigación Necesaria:**
```javascript
// En consola del navegador (F12):
const checkboxes = document.querySelectorAll(`input[data-sheet="hoja2"][data-column]`);
console.log('Total checkboxes encontrados:', checkboxes.length);
checkboxes.forEach((cb, index) => {
    console.log(`${index + 1}. ID: ${cb.id}, Column: ${cb.dataset.column}`);
});
```

**Hipótesis:**
- Si muestra 21 checkboxes cuando solo hay 7 columnas, significa que hay **3 copias de cada checkbox** (7 x 3 = 21)
- Posible causa: El template está siendo renderizado múltiples veces para la misma hoja

---

### 🟡 **Problema 2: Checkboxes de Configuración No Visibles al Seleccionar Individualmente**

**Síntoma:** Los checkboxes "Permitir NULL" solo aparecen al usar "Seleccionar todo".

**Causa Identificada:**
La función `updateColumnSelection()` **YA ESTÁ** implementada para mostrar los campos al seleccionar individuales. El problema puede ser:

1. **Error en el selector JavaScript:**
   ```javascript
   const configRow = document.getElementById(`config-${sheetSlug}-${counter}`);
   ```
   Si `sheetSlug` o `counter` no coinciden con los IDs del HTML, no encontrará el elemento.

2. **Problema con el `display` inicial:**
   Los elementos tienen `style="display: none;"` y puede que no se estén mostrando correctamente.

**Verificación:**
```javascript
// En consola:
const checkbox = document.getElementById('col-hoja2-1');
checkbox.checked = true;
updateColumnSelection('hoja2');

// Verificar si se mostró el config:
const configRow = document.getElementById('config-hoja2-1');
console.log('ConfigRow:', configRow);
console.log('Display:', configRow ? configRow.style.display : 'NO ENCONTRADO');
```

---

### 🔴 **Problema 3: Vista Previa Muestra Dicts en Lugar de Datos**

**Síntoma:** Las celdas muestran:
```
{'renamed_to': 'fecha', 'sql_type': 'NVARCHAR(255)', 'nullable': False, 'default_value': "' '"}
```

**Causa Probable:**
Esto sucede cuando:
1. Un proceso ya guardado tiene `column_mappings` configurados
2. Al cargar el proceso existente, el template está mostrando `column_mappings` en lugar de `preview.sample_data`
3. Hay confusión entre los datos de configuración y los datos reales

**Ubicación del Bug:**
Probablemente en el template cuando se carga un proceso existente (editar proceso).

**Investigación Necesaria:**
- Revisar si la vista `list_excel_multi_sheet_columns` está siendo llamada para editar un proceso existente
- Verificar si `sheets_data` está siendo sobrescrito por `column_mappings` del proceso guardado

---

### 🔴 **Problema 4: Error al Ejecutar Proceso "Múltiples tablas creadas (0 exitosas)"**

**Síntoma:** Error genérico sin detalles.

**Causa Probable:**
1. **Duplicación de columnas** está causando que el SQL CREATE TABLE falle
2. **Column_mappings mal formateados** (dicts en lugar de strings simples)
3. **Falta de try-catch con traceback** en el código de ejecución

**Ubicaciones a Revisar:**
- `models.py` → método `run()` o `_process_excel_sheets_individually()`
- Necesita agregar logging detallado con `traceback.format_exc()`

---

## 🔧 Correcciones Implementadas

### ✅ **Corrección 1: Detectar y Prevenir Duplicados en el Selector**

Voy a agregar validación en el frontend para detectar duplicados:

```javascript
function updateColumnSelection(sheetName) {
    const checkboxes = document.querySelectorAll(`input[data-sheet="${sheetName}"][data-column]`);
    const selected = [];
    const seenColumns = new Set();  // 🆕 NUEVO: Prevenir duplicados
    
    // Calcular el slug de la hoja UNA VEZ fuera del loop
    const sheetSlug = sheetName.replace(/[^a-zA-Z0-9]/g, '-').toLowerCase();
    
    // 🆕 NUEVO: Detectar duplicados en el DOM
    checkboxes.forEach(checkbox => {
        const columnName = checkbox.dataset.column;
        if (seenColumns.has(columnName)) {
            console.warn(`⚠️ DUPLICADO DETECTADO: Columna "${columnName}" aparece múltiples veces para hoja "${sheetName}"`);
            console.warn(`   Checkbox ID: ${checkbox.id}`);
        }
        seenColumns.add(columnName);
    });
    
    // Continuar con la lógica normal...
}
```

### ✅ **Corrección 2: Asegurar que los Campos de Configuración Aparezcan**

Voy a agregar debugging adicional y mejorar la función:

```javascript
if (configRow) {
    if (isChecked) {
        // Columna seleccionada: mostrar configuración
        configRow.style.display = 'flex';
        console.log(`✅ Mostrando config para: ${columnName} (counter: ${counter})`);
        
        if (nullableCheckbox) {
            nullableCheckbox.disabled = false;
        }
        
        // Establecer placeholder dinámico según tipo SQL
        if (defaultInput) {
            const sqlType = defaultInput.dataset.sqlType;
            const contextualPlaceholder = getPlaceholderForType(sqlType);
            defaultInput.placeholder = contextualPlaceholder;
        }
        
        // Inicializar tooltips de Bootstrap para los nuevos elementos visibles
        initializeTooltips();
    } else {
        // Columna NO seleccionada: ocultar y resetear configuración
        configRow.style.display = 'none';
        console.log(`❌ Ocultando config para: ${columnName}`);
        // ... resto del código
    }
} else {
    console.error(`❌ NO SE ENCONTRÓ configRow para: config-${sheetSlug}-${counter}`);
    console.error(`   Hoja: ${sheetName}, Columna: ${columnName}, Checkbox ID: ${checkboxId}`);
}
```

### ✅ **Corrección 3: Separar Vista Previa de Metadatos**

El template ya está correcto. El problema es cuando se carga un proceso existente. Necesito asegurar que `sheets_data` contenga los datos reales, no `column_mappings`.

**Solución en views.py:**
```python
def list_excel_multi_sheet_columns(request, source_id, process_id=None):
    """Nueva vista integrada para selección de hojas y columnas de Excel"""
    source = get_object_or_404(DataSource, pk=source_id)
    
    # ... código existente ...
    
    # Obtener datos completos de cada hoja: columnas y vista previa
    sheets_data = {}
    for sheet in sheets:
        columns = processor.get_sheet_columns(sheet)  # ✅ SIEMPRE obtener del Excel
        preview = processor.get_sheet_preview(sheet)  # ✅ SIEMPRE obtener del Excel
        
        sheets_data[sheet] = {
            'columns': columns,  # ✅ Lista de dicts con name, type, sql_type
            'preview': preview,  # ✅ Dict con sample_data (lista de listas)
            'total_rows': preview.get('total_rows', 0) if preview else 0,
            'column_count': len(columns) if columns else 0
        }
    
    context = {
        'source': source,
        'sheets': sheets,
        'sheets_data': sheets_data,  # ✅ NUNCA pasar column_mappings aquí
    }
    
    # 🆕 Si estamos editando un proceso, cargar column_mappings por separado
    if process_id:
        process = get_object_or_404(MigrationProcess, pk=process_id)
        context['existing_process'] = process
        context['column_mappings'] = process.column_mappings  # ✅ Separado de sheets_data
    
    return render(request, 'automatizacion/excel_multi_sheet_selector.html', context)
```

### ✅ **Corrección 4: Mejorar Logging de Errores en Ejecución**

En `models.py`, método `run()` o `_process_excel_sheets_individually()`:

```python
import traceback

def run(self):
    """Ejecuta el proceso de migración"""
    try:
        self.status = 'running'
        self.save()
        
        # ... código de ejecución ...
        
        self.status = 'completed'
        self.last_run = timezone.now()
        self.save()
        
    except Exception as e:
        self.status = 'failed'
        self.save()
        
        # 🆕 NUEVO: Logging detallado
        error_details = {
            'error_type': type(e).__name__,
            'error_message': str(e),
            'traceback': traceback.format_exc(),
            'process_id': self.id,
            'process_name': self.name,
            'selected_sheets': self.selected_sheets,
            'selected_columns': self.selected_columns,
        }
        
        logger.error(f"❌ Error ejecutando proceso {self.id}: {error_details}")
        
        # Registrar en MigrationLog
        MigrationLog.objects.create(
            process=self,
            level='error',
            stage='execution',
            message=f"Error en ejecución: {str(e)}",
            details=error_details
        )
        
        raise  # Re-raise para que el usuario vea el error
```

---

## 🧪 Plan de Testing

### **Test 1: Verificar Duplicación**
```
1. Abrir Excel con 7 columnas en Hoja 2
2. Ir a multi-config
3. Abrir consola (F12)
4. Ejecutar:
   const checkboxes = document.querySelectorAll(`input[data-sheet="hoja2"][data-column]`);
   console.log('Total:', checkboxes.length);  // Esperado: 7, no 21
5. Si hay duplicados, revisar el HTML generado (buscar inputs duplicados)
```

### **Test 2: Verificar Checkboxes Individuales**
```
1. Marcar UNA SOLA columna (no usar "Seleccionar todo")
2. Verificar que aparecen los campos:
   - ☐ Permitir NULL
   - Valor por defecto: [   ] 💡
3. Si no aparecen, revisar consola por errores de "NO SE ENCONTRÓ configRow"
```

### **Test 3: Verificar Vista Previa**
```
1. Abrir Excel multi-config
2. Verificar que la tabla de vista previa muestra:
   - Columnas: fecha, codigo, cantidad, etc.
   - Filas con datos reales: 2024-01-15, P001, 5, etc.
   - NO debe mostrar: {'renamed_to': ...}
3. Si muestra dicts, verificar que sheets_data no está contaminado por column_mappings
```

### **Test 4: Verificar Ejecución de Proceso**
```
1. Configurar proceso con 3 hojas, 5 columnas cada una
2. Guardar configuración
3. Ejecutar proceso
4. Si falla, revisar logs en:
   - Consola del servidor (terminal donde corre Django)
   - Tabla MigrationLog en la DB
   - Debe mostrar SQL ejecutado y traceback completo
```

---

## 📝 Resumen de Archivos a Modificar

| Archivo | Cambio | Prioridad |
|---------|--------|-----------|
| `excel_multi_sheet_selector.html` | Agregar debug logging en `updateColumnSelection()` | 🔴 Alta |
| `excel_multi_sheet_selector.html` | Agregar detección de duplicados en `updateColumnSelection()` | 🔴 Alta |
| `views.py` | Asegurar que `sheets_data` no contenga `column_mappings` | 🟡 Media |
| `models.py` | Agregar traceback completo en manejo de errores | 🔴 Alta |
| `utils.py` | Verificar que `get_sheet_columns()` no devuelve duplicados | 🟡 Media |

---

## 🎯 Próximos Pasos

1. ✅ Implementar logging de debugging
2. ✅ Agregar detección de duplicados
3. ✅ Mejorar manejo de errores con traceback
4. ⏳ Probar con Excel real
5. ⏳ Verificar que la corrección funciona en todos los casos

---

**Fecha de Análisis:** 22 de octubre de 2024  
**Estado:** Análisis completo, correcciones pendientes de implementación
