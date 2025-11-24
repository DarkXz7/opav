# 🎯 Guía Rápida: Cómo Diagnosticar los 4 Bugs

## 🚀 Inicio Rápido

### **Paso 1: Abrir la Aplicación**
1. Ejecuta el servidor Django: `python manage.py runserver`
2. Navega a: `http://localhost:8000/automatizacion/`
3. Selecciona tu fuente de datos Excel
4. Haz clic en "Configurar Multi-Hoja"

### **Paso 2: Abrir Consola del Navegador**
1. Presiona **F12** (o Ctrl+Shift+I)
2. Ve a la pestaña **"Console"**
3. Deja la consola abierta para ver los mensajes de debugging

---

## 🐛 Diagnóstico de Cada Bug

### **Bug #1: Duplicación de Columnas (21 en vez de 7)**

#### 🔍 Cómo verificar:
1. En la página multi-config, localiza **"Hoja 2"** (o la hoja con 7 columnas)
2. Haz clic en el botón **"Seleccionar todo"**
3. **Mira la consola** inmediatamente

#### ✅ Qué esperar en la consola:

**Si NO hay duplicados (funcionando correctamente):**
```
🔍 DEBUG selectAllColumns("hoja2"):
   Checkboxes encontrados ANTES: 7
   Checkboxes marcados: 7
```

**Si HAY duplicados (bug presente):**
```
🔍 DEBUG selectAllColumns("hoja2"):
   Checkboxes encontrados ANTES: 21
❌ DUPLICADOS DETECTADOS:
   - "fecha": aparece 3 veces
   - "codigo": aparece 3 veces
   - "cantidad": aparece 3 veces
   ...

❌ TOTAL DE DUPLICADOS ENCONTRADOS: 14
   Columnas únicas: 7
   Checkboxes totales: 21
   Ratio: 3x duplicación
```

#### 📋 Siguiente acción:
- **Si hay 21 checkboxes:** El problema está en el **backend** (template genera HTML duplicado)
  - → Revisar `excel_multi_sheet_selector.html` líneas 362-380 (loop de columnas)
  - → Revisar `views.py` línea 375+ (`list_excel_multi_sheet_columns`)
  
- **Si hay 7 checkboxes pero se marcan 21:** El problema está en el **frontend** (JavaScript duplica selecciones)
  - → Revisar JavaScript de `selectAllColumns()` y `updateColumnSelection()`

---

### **Bug #2: Checkboxes "Permitir NULL" No Visibles al Seleccionar Individual**

#### 🔍 Cómo verificar:
1. **NO uses "Seleccionar todo"**
2. Marca **UNA SOLA** columna haciendo clic en su checkbox
3. **Mira la consola** y **mira debajo de la columna marcada**

#### ✅ Qué esperar:

**En la consola:**
```
✅ Columna seleccionada: "fecha" (counter: 1)
   configRow encontrado: true
   nullableCheckbox encontrado: true
   defaultInput encontrado: true
   ✅ configRow.display = 'flex' para "fecha"
```

**En la página:**
Debería aparecer debajo de la columna:
```
☑ Permitir NULL  ℹ️
Valor por defecto: [___________] 💡
```

**Si NO aparecen los campos (bug presente):**
```
❌ NO SE ENCONTRÓ configRow para: config-hoja2-1
   Hoja: "hoja2" → Slug: "hoja2"
   Columna: "fecha", Checkbox ID: "col-hoja2-1"
```

#### 📋 Siguiente acción:
- Si los elementos NO se encuentran, el problema es que el **ID no coincide**
  - → Verificar que el HTML tiene: `<div id="config-hoja2-1">`
  - → Verificar que JavaScript busca: `document.getElementById('config-hoja2-1')`
  - → Verificar que el `counter` se calcula correctamente: `checkboxId.split('-').pop()`

---

### **Bug #3: Vista Previa Muestra Dicts en Lugar de Datos**

#### 🔍 Cómo verificar:
1. En la página multi-config, localiza la sección **"Vista previa de datos"**
2. Observa las celdas de la tabla

#### ✅ Qué esperar:

**Datos correctos (funcionando):**
```
| Columna      | fecha       | codigo | cantidad |
|--------------|-------------|--------|----------|
| Tipo         | DATE        | VARCHAR| INT      |
| Muestra      | 2024-01-15  | P001   | 5        |
|              | 2024-01-16  | P002   | 10       |
|              | 2024-01-17  | P003   | 15       |
```

**Datos incorrectos (bug presente):**
```
| Columna      | fecha                                            |
|--------------|--------------------------------------------------|
| Muestra      | {'renamed_to': 'fecha', 'sql_type': 'DATE', ... }|
|              | {'renamed_to': 'fecha', 'sql_type': 'DATE', ... }|
```

#### 📋 Siguiente acción:
- Si muestra dicts, significa que `column_mappings` está contaminando `preview.sample_data`
  - → Verificar si la URL tiene `?process_id=XX`
  - → Revisar `views.py` para asegurar que `sheets_data` usa `preview.sample_data` (lista de listas)
  - → NO debe usar `column_mappings` en el preview

---

### **Bug #4: Error al Ejecutar "Múltiples tablas creadas (0 exitosas)"**

#### 🔍 Cómo verificar:
1. Configura un proceso multi-hoja (selecciona hojas y columnas)
2. Haz clic en **"Guardar Configuración"**
3. Haz clic en **"Ejecutar Proceso"**
4. **Mira la terminal del servidor Django** (donde corre `runserver`)

#### ✅ Qué esperar:

**Si hay error (bug presente), verás:**
```
================================================================================
❌ ERROR CRÍTICO EJECUTANDO PROCESO: Proceso Multi-Hoja (ID: 74)
================================================================================
🔴 Tipo de error: KeyError
🔴 Mensaje: 'columna_desconocida'

📋 CONTEXTO DEL PROCESO:
   - Source Type: excel
   - Selected Tables: None
   - Selected Sheets: ['Hoja 2', 'Hoja 3']
   - Selected Columns: {'Hoja 2': ['fecha', 'codigo', 'cantidad'], 'Hoja 3': [...]}
   - Column Mappings: {'Hoja 2': {'fecha': {'renamed_to': 'fecha_registro', ...}}}

🔍 TRACEBACK COMPLETO:
Traceback (most recent call last):
  File ".../models.py", line 350, in run
    success, result_info = self._process_excel_sheets_individually(...)
  File ".../models.py", line 850, in _process_excel_sheets_individually
    df = df[selected_cols]
KeyError: "['columna_desconocida'] not found in axis"
================================================================================
```

#### 📋 Siguiente acción:
- Con el **traceback completo**, ahora puedes ver:
  1. **Línea exacta** donde falló (ej: `models.py:850`)
  2. **Datos exactos** que causaron el fallo (en "CONTEXTO DEL PROCESO")
  3. **Tipo de error** (`KeyError`, `TypeError`, etc.)
  
- Las causas comunes son:
  - `selected_columns` contiene nombres de columnas que no existen en el Excel
  - `column_mappings` tiene formato incorrecto (dict cuando debería ser string)
  - Nombres de columnas con espacios o caracteres especiales no coinciden

---

## 📊 Resumen Visual de Diagnóstico

| Bug | Dónde mirar | Qué buscar | Corrección |
|-----|-------------|------------|------------|
| **#1 Duplicados** | Consola (F12) | `Checkboxes encontrados ANTES: 21` vs `7` | Backend si 21 en HTML, Frontend si 7 marcados como 21 |
| **#2 Checkboxes no visibles** | Consola + Página | `configRow encontrado: false` + campos no aparecen | Verificar IDs en HTML vs JavaScript |
| **#3 Preview con dicts** | Tabla de preview | Celdas muestran `{'renamed_to': ...}` | Separar column_mappings de preview.sample_data |
| **#4 Error ejecución** | Terminal del servidor | Traceback completo con contexto | Corregir datos según error específico |

---

## 🔧 Herramientas de Debugging Agregadas

### **En el Frontend (JavaScript):**
✅ `updateColumnSelection()`: Detecta duplicados, reporta elementos no encontrados
✅ `selectAllColumns()`: Cuenta checkboxes, detecta duplicados por columna
✅ `console.log/warn/error`: Mensajes detallados con emojis para fácil identificación

### **En el Backend (Python):**
✅ `models.py → run()`: Traceback completo con contexto del proceso
✅ Error details dict: tipo_error, mensaje, traceback, selected_columns, column_mappings
✅ Logging formateado: Separadores visuales (=====), emojis, información estructurada

---

## 🎬 Flujo de Trabajo Recomendado

1. **Primero:** Ejecuta Test #1 (Duplicados) → Abre consola y haz clic en "Seleccionar todo"
2. **Segundo:** Ejecuta Test #2 (Checkboxes) → Marca UNA columna y verifica que aparecen los campos
3. **Tercero:** Ejecuta Test #3 (Preview) → Verifica que muestra datos reales, no dicts
4. **Cuarto:** Ejecuta Test #4 (Ejecución) → Ejecuta el proceso y captura el traceback

5. **Comparte los resultados conmigo:**
   - Screenshot de la consola (F12)
   - Copiar/pegar el traceback de la terminal
   - Descripción de qué ves vs qué esperabas

6. **Basado en los resultados**, aplicaremos las correcciones específicas

---

## 💡 Tips Adicionales

### **Para limpiar la consola:**
- En Chrome/Edge: Haz clic derecho → "Clear console" o presiona Ctrl+L

### **Para copiar el traceback completo:**
- En Windows: Selecciona el texto en terminal → Clic derecho → Copiar
- Pega en un archivo .txt o en el chat

### **Para ver más detalles:**
- Si la consola tiene muchos mensajes, busca por:
  - `❌` (errores)
  - `⚠️` (warnings)
  - `🔍 DEBUG` (mensajes de debugging)

---

**¿Listo para probar?** 🚀

1. Abre la aplicación
2. Abre la consola (F12)
3. Haz clic en "Seleccionar todo"
4. Copia y pega lo que ves en la consola

¡Con esa información podré decirte exactamente qué está pasando! 👍
