# 👀 Guía Visual: Dónde Ver los Nuevos Campos en el Frontend

## 🎯 Ubicación Exacta

**URL:**
```
http://localhost:8000/automatizacion/excel/<ID_DEL_PROCESO>/multi-config/
```

**Ejemplo:**
```
http://localhost:8000/automatizacion/excel/5/multi-config/
```

---

## 📸 Capturas Esperadas (Descripción Visual)

### **VISTA INICIAL (sin columnas seleccionadas):**

```
┌─────────────────────────────────────────────────────────┐
│ 📊 Configuración Multi-Hoja: MiProcesoExcel            │
├─────────────────────────────────────────────────────────┤
│ Pestañas: [Sheet1] [Sheet2] [Sheet3]                   │
├─────────────────────────────────────────────────────────┤
│ Columnas disponibles:                                   │
│                                                         │
│ ☐ fecha (DATETIME2)                                    │
│    [fecha]  ← Input deshabilitado (gris)               │
│                                                         │
│ ☐ codigo (VARCHAR(50))                                 │
│    [codigo]  ← Input deshabilitado (gris)              │
│                                                         │
│ ☐ cantidad (INT)                                       │
│    [cantidad]  ← Input deshabilitado (gris)            │
└─────────────────────────────────────────────────────────┘
```

**❌ NO verás configuración de NULL/Default porque ninguna columna está seleccionada**

---

### **DESPUÉS DE SELECCIONAR UNA COLUMNA:**

```
┌─────────────────────────────────────────────────────────┐
│ 📊 Configuración Multi-Hoja: MiProcesoExcel            │
├─────────────────────────────────────────────────────────┤
│ Columnas disponibles:                                   │
│                                                         │
│ ☑ fecha (DATETIME2)  ← MARCADO                         │
│    Nombre en destino: [fecha]  ← Habilitado            │
│                                                         │
│    ┌─────────────────────────────────────────────┐    │
│    │ ☐ Permitir NULL                              │    │  ← NUEVO
│    │                                               │    │
│    │ Valor por defecto: [GETDATE()]  💡          │    │  ← NUEVO
│    │ Si el Excel está vacío, usar este valor     │    │
│    └─────────────────────────────────────────────┘    │
│                                                         │
│ ☐ codigo (VARCHAR(50))                                 │
│    [codigo]  ← Input deshabilitado (gris)              │
│                                                         │
│ ☐ cantidad (INT)                                       │
│    [cantidad]  ← Input deshabilitado (gris)            │
└─────────────────────────────────────────────────────────┘
```

**✅ Ahora SÍ verás la configuración de NULL/Default para la columna "fecha"**

---

### **CON MÚLTIPLES COLUMNAS SELECCIONADAS:**

```
┌─────────────────────────────────────────────────────────┐
│ ☑ fecha (DATETIME2)                                    │
│    Nombre en destino: [fecha]                          │
│    ☐ Permitir NULL                                     │
│    Valor por defecto: [GETDATE()]  💡                  │
│    Si el Excel está vacío, usar este valor            │
│                                                         │
│ ☑ codigo (VARCHAR(50))                                 │
│    Nombre en destino: [codigo]                         │
│    ☐ Permitir NULL                                     │
│    Valor por defecto: [SIN_CODIGO]  💡                 │
│    Si el Excel está vacío, usar este valor            │
│                                                         │
│ ☑ cantidad (INT)                                       │
│    Nombre en destino: [cantidad]                       │
│    ☐ Permitir NULL                                     │
│    Valor por defecto: [0]  💡                          │
│    Si el Excel está vacío, usar este valor            │
│                                                         │
│ ☐ precio (FLOAT)  ← NO seleccionada                   │
│    [precio]  ← Input deshabilitado                     │
│    [Configuración NO visible]                          │
└─────────────────────────────────────────────────────────┘
```

---

## 🎨 Estados Visuales del Checkbox "Permitir NULL"

### **Estado 1: Nullable MARCADO (por defecto)**

```
☑ Permitir NULL
Valor por defecto: [NULL]  💡  ← Input DESHABILITADO (gris)
```

**Significado:** La columna acepta valores NULL. No necesita valor por defecto.

---

### **Estado 2: Nullable DESMARCADO**

```
☐ Permitir NULL
Valor por defecto: [        ]  💡  ← Input HABILITADO (blanco)
```

**Significado:** La columna NO acepta NULL. REQUIERE un valor por defecto.

---

## 💡 Funcionalidad del Botón de Sugerencia

### **Antes de hacer click en 💡:**

```
☐ Permitir NULL
Valor por defecto: [        ]  💡  ← Campo vacío
```

### **Después de hacer click en 💡:**

```
☐ Permitir NULL
Valor por defecto: [0]  💡  ← Valor sugerido automáticamente
```

**Sugerencias según tipo:**
- `INT` → `0`
- `DECIMAL` → `0.00`
- `BIT` → `1`
- `VARCHAR` → `' '`
- `DATE` → `GETDATE()`

---

## 🔍 Cómo Verificar que Funciona

### **1. Abre la Consola del Navegador (F12)**

Ve a la pestaña "Console" y busca estos mensajes cuando selecciones una columna:

```javascript
// Si NO encuentra el elemento:
⚠️ No se encontró configRow para: config-sheet1-1

// Si SÍ encuentra el elemento:
✅ (No habrá warnings, el elemento se mostrará)
```

---

### **2. Inspecciona el HTML (Botón derecho → Inspeccionar)**

Busca este HTML cuando tengas una columna seleccionada:

```html
<div class="row align-items-center mt-2 ms-4" 
     id="config-sheet1-1" 
     style="display: flex;">  ← Debe ser "flex", NO "none"
     
    <div class="col-md-3">
        <div class="form-check">
            <input class="form-check-input column-nullable-checkbox" 
                   type="checkbox" 
                   id="nullable-sheet1-1">
            <label>Permitir NULL</label>
        </div>
    </div>
    
    <div class="col-md-9">
        <input type="text" 
               id="default-sheet1-1" 
               placeholder="Ej: 0, ' ', GETDATE()">
        <button id="suggest-sheet1-1">💡</button>
    </div>
</div>
```

**Clave:** `style="display: flex;"` significa que SÍ está visible.

---

### **3. Verifica IDs en la Consola**

Ejecuta esto en la consola del navegador:

```javascript
// Obtener la primera columna seleccionada
const checkbox = document.querySelector('input[data-column]');
console.log('Checkbox ID:', checkbox.id);
// Esperado: "col-sheet1-1" o similar

// Buscar el configRow correspondiente
const counter = checkbox.id.split('-').pop();
const sheetSlug = 'sheet1'; // Ajusta según tu hoja
const configRow = document.getElementById(`config-${sheetSlug}-${counter}`);
console.log('ConfigRow encontrado:', configRow);
// Esperado: <div id="config-sheet1-1">...</div>

console.log('Display style:', configRow ? configRow.style.display : 'NO ENCONTRADO');
// Esperado: "flex" (visible) o "none" (oculto)
```

---

## 🐛 Troubleshooting

### **Problema 1: No veo ningún campo extra**

**Posible Causa 1:** El servidor Django no está corriendo con los cambios
```powershell
# Detener servidor (Ctrl+C)
# Reiniciar
python manage.py runserver
```

**Posible Causa 2:** Caché del navegador
```
Ctrl + Shift + R (Chrome/Firefox)
Ctrl + F5 (Edge)
```

**Posible Causa 3:** No has seleccionado una columna
```
✅ Marca el checkbox de una columna primero
```

---

### **Problema 2: Los campos aparecen pero están deshabilitados**

**Diagnóstico en Consola (F12):**
```javascript
const defaultInput = document.getElementById('default-sheet1-1');
console.log('Input deshabilitado:', defaultInput.disabled);
// Esperado: true (si nullable está marcado) o false (si nullable NO está marcado)

const nullableCheckbox = document.getElementById('nullable-sheet1-1');
console.log('Nullable marcado:', nullableCheckbox.checked);
// Esperado: false (para habilitar el input de default)
```

**Solución:**
- Desmarca el checkbox "Permitir NULL"
- El campo "Valor por defecto" se habilitará automáticamente

---

### **Problema 3: El botón 💡 no hace nada**

**Verificación:**
```javascript
// En la consola del navegador
suggestDefaultValue('sheet1', '1', 'INT');
// Debería rellenar el campo con "0"
```

**Si no funciona:**
1. Verifica errores en la consola (F12 → Console)
2. Busca mensajes como: `ReferenceError: suggestDefaultValue is not defined`
3. Si aparece, significa que el JS no se cargó correctamente

---

### **Problema 4: Los campos desaparecen al desmarcar la columna**

✅ **Esto es CORRECTO**. Es el comportamiento esperado:
- Columna SELECCIONADA → Configuración VISIBLE
- Columna DESELECCIONADA → Configuración OCULTA

---

## 📝 Checklist de Verificación

Antes de probar, asegúrate de:

- [ ] Servidor Django está corriendo (`python manage.py runserver`)
- [ ] Has hecho Ctrl+Shift+R para limpiar caché
- [ ] Estás en la URL correcta: `/automatizacion/excel/<ID>/multi-config/`
- [ ] Has seleccionado AL MENOS UNA HOJA (pestaña superior)
- [ ] Has MARCADO al menos un checkbox de columna
- [ ] Has revisado la consola del navegador (F12) en busca de errores

---

## 🎬 Pasos para Ver los Campos (Tutorial)

1. **Abrir proceso Excel:**
   ```
   http://localhost:8000/automatizacion/excel/5/multi-config/
   ```

2. **Hacer click en una pestaña de hoja:**
   ```
   [Sheet1]  ← Click aquí
   ```

3. **Marcar el checkbox de una columna:**
   ```
   ☐ fecha (DATETIME2)  ← Click aquí para marcar
   ```

4. **Observar que aparece la sección de configuración debajo:**
   ```
   ☐ Permitir NULL
   Valor por defecto: [        ]  💡
   ```

5. **Desmarcar "Permitir NULL":**
   ```
   ☐ Permitir NULL  ← Click aquí para desmarcar
   ```

6. **Hacer click en 💡:**
   ```
   Valor por defecto: [GETDATE()]  💡  ← El campo se rellena automáticamente
   ```

---

## 🚨 Si Aún No Ves Nada

Ejecuta esto en la consola del navegador (F12):

```javascript
// 1. Verificar que existe el elemento
const configRow = document.querySelector('[id^="config-"]');
console.log('Primer configRow encontrado:', configRow);

// 2. Verificar su visibilidad
if (configRow) {
    console.log('Display:', configRow.style.display);
    console.log('HTML:', configRow.innerHTML);
} else {
    console.log('❌ NO SE ENCONTRÓ NINGÚN configRow');
}

// 3. Listar todos los configRows
const allConfigRows = document.querySelectorAll('[id^="config-"]');
console.log(`Total de configRows: ${allConfigRows.length}`);
allConfigRows.forEach((row, index) => {
    console.log(`${index + 1}. ID: ${row.id}, Display: ${row.style.display}`);
});
```

**Envíame el output de esta consola y te ayudo a diagnosticar el problema.**

---

¿Te aparecen ahora los campos? Si no, ejecuta el script de diagnóstico de arriba y compárteme el resultado. 🔍
