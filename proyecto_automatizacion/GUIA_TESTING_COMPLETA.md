# 🧪 GUÍA DE TESTING - SISTEMA DE VALIDACIÓN

**Objetivo**: Verificar que todos los cambios implementados funcionan correctamente

---

## ⚡ TESTING RÁPIDO (5 minutos)

### 1. Iniciar servidor Django

```powershell
cd "c:\Users\migue\OneDrive\Escritorio\DJANGO DE NUEVO\opav\proyecto_automatizacion"
python manage.py runserver
```

### 2. Verificar que no hay errores de importación

✅ **Esperado**: Servidor inicia sin errores

```
Django version 4.2.23, using settings 'proyecto_automatizacion.settings'
Starting development server at http://127.0.0.1:8000/
Quit the server with CTRL-BREAK.
```

❌ **Si hay error de import**: Revisar que `legacy_utils.py` existe

---

### 3. Test de redirect directo

```
1. Ir a http://127.0.0.1:8000/automatizacion/
2. Click en "Subir archivo Excel"
3. Seleccionar un archivo Excel de prueba
4. Click en "Subir"
```

✅ **Esperado**: Redirige DIRECTAMENTE a `/automatizacion/excel/<id>/multi-config/`

❌ **Si redirige a /sheets/**: Verificar `views.py` línea 301

---

### 4. Test de inferencia de tipos

```
1. En la página /multi-config/
2. Abrir DevTools (F12)
3. Ver la pestaña "Console"
```

✅ **Esperado**: Logs como:
```
🚀 Sistema de validación e inferencia cargado
Hoja 'Hoja1': 5 columnas, nombre sugerido: 'hoja1'
```

❌ **Si no hay logs**: Verificar que `validation_and_inference.js` está cargado

---

## 🔬 TESTING DETALLADO (30 minutos)

### Test 1: Endpoint validate-sheet-rename

#### Usando PowerShell

```powershell
# Obtener CSRF token primero
$response = Invoke-WebRequest -Uri "http://127.0.0.1:8000/automatizacion/" -SessionVariable session

$csrfToken = ($response.Content | Select-String -Pattern 'csrfmiddlewaretoken.*value="([^"]+)"').Matches.Groups[1].Value

# Hacer request al endpoint
$headers = @{
    "Content-Type" = "application/json"
    "X-CSRFToken" = $csrfToken
    "Referer" = "http://127.0.0.1:8000/"
}

$body = @{
    new_name = "Ventas 2024!"
    existing_names = @()
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://127.0.0.1:8000/automatizacion/api/validate-sheet-rename/" `
                  -Method POST `
                  -Headers $headers `
                  -Body $body `
                  -WebSession $session
```

✅ **Esperado**:
```json
{
    "valid": true,
    "normalized": "ventas_2024",
    "error": null
}
```

#### Casos de prueba

| Input | Esperado | Razón |
|-------|----------|-------|
| `"Ventas 2024"` | `ventas_2024` | Espacios → guiones bajos |
| `"Año 2024"` | `ano_2024` | Ñ → n |
| `"Cliente!!!"` | `cliente` | Símbolos eliminados |
| `"___test___"` | `test` | Guiones bajos al inicio/final eliminados |
| `""` (vacío) | Error | Nombre vacío no válido |
| `"123"` | Error | No puede empezar con número |

---

### Test 2: Endpoint infer-types

```powershell
# Crear Excel de prueba primero
# (Usar crear_excel_prueba_normalizacion.py si existe)

# Subir Excel y obtener source_id
# Luego hacer request:

$body = @{
    sheet_name = "Hoja1"
    columns = @("edad", "nombre", "salario")
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://127.0.0.1:8000/automatizacion/api/excel/1/infer-types/" `
                  -Method POST `
                  -Headers $headers `
                  -Body $body `
                  -WebSession $session
```

✅ **Esperado**:
```json
{
    "types": {
        "edad": {
            "sql_type": "TINYINT",
            "confidence": 1.0,
            "nullable": false,
            "default_value": "0",
            "warnings": []
        },
        "nombre": {
            "sql_type": "NVARCHAR(50)",
            "confidence": 0.95,
            "nullable": true,
            "default_value": null,
            "warnings": []
        },
        "salario": {
            "sql_type": "FLOAT",
            "confidence": 1.0,
            "nullable": false,
            "default_value": "0.0",
            "warnings": []
        }
    }
}
```

---

### Test 3: JavaScript validation functions

Abrir DevTools Console en la página `/multi-config/`:

```javascript
// Test 1: Validación de valores por defecto
validateDefaultValue('42', 'INT')
// ✅ Esperado: {valid: true, error: null}

validateDefaultValue('abc', 'INT')
// ✅ Esperado: {valid: false, error: "Debe ser un número entero"}

validateDefaultValue('3.14', 'FLOAT')
// ✅ Esperado: {valid: true, error: null}

validateDefaultValue('GETDATE()', 'DATETIME')
// ✅ Esperado: {valid: true, error: null}

// Test 2: Placeholder dinámico
const input = document.createElement('input');
updatePlaceholderForType(input, 'INT');
console.log(input.placeholder);
// ✅ Esperado: "0"

updatePlaceholderForType(input, 'DATE');
console.log(input.placeholder);
// ✅ Esperado: "GETDATE()"

// Test 3: Validación AJAX de renombrado
validateSheetRename('Hoja1', 'Ventas 2024!', [])
    .then(result => console.log(result));
// ✅ Esperado: {valid: true, normalized: "ventas_2024", error: null}
```

---

### Test 4: Flujo completo de guardado

```
1. Subir Excel de prueba
2. En /multi-config/:
   - Marcar checkbox de columna "edad"
   - Verificar que se muestra configuración
   - Verificar que tipo sugerido es "TINYINT"
   - Cambiar a "INT"
   - Verificar que placeholder cambia a "0"
   - Escribir "abc" en default
   - Blur del input
   - ✅ Esperado: Border rojo + mensaje "Debe ser un número entero"
   
3. Corregir a "18"
   - ✅ Esperado: Border verde
   
4. Click en "Guardar Proceso"
   - Nombre: "Test Validación"
   - ✅ Esperado: Guardado exitoso
   
5. Verificar en base de datos:
```

```python
# En Django shell
python manage.py shell

from automatizacion.models import MigrationProcess
p = MigrationProcess.objects.get(name="Test Validación")
print(p.type_configuration)  # ✅ Esperado: JSONField con tipos
print(p.types_inferred_at)    # ✅ Esperado: Timestamp
print(p.column_mappings)       # ✅ Esperado: Configuración guardada
```

---

### Test 5: Normalización en guardado

```python
# Crear proceso de prueba con datos problemáticos
import pandas as pd

# Excel con datos "sucios"
data = {
    'edad': [25, '30', 'N/A', 35],  # Mezcla de int y string
    'activo': [1, 'true', 'sí', 0]   # Mezcla de formatos booleanos
}
df = pd.DataFrame(data)
df.to_excel('test_sucio.xlsx', index=False)

# Subir este Excel
# Configurar columnas con tipos estrictos
# Guardar proceso
# Ejecutar proceso
```

✅ **Esperado en logs**:
```
⚠️ Advertencias de normalización en 'tabla_test':
  • Columna 'edad': 1 valores inválidos convertidos a NULL
    Ejemplo: 'N/A'
  • Columna 'activo': 2 valores normalizados
    Ejemplo: 'sí' → 1
```

---

## 🐛 DEBUGGING

### Error: JavaScript no carga

**Síntoma**: No hay logs en consola, funciones no definidas

**Solución**:
```
1. Verificar que existe:
   automatizacion/static/automatizacion/js/validation_and_inference.js

2. En template, verificar:
   <script src="{% static 'automatizacion/js/validation_and_inference.js' %}"></script>

3. Ejecutar collectstatic:
   python manage.py collectstatic --noinput
```

---

### Error: Endpoint 404

**Síntoma**: POST a /api/validate-sheet-rename/ retorna 404

**Solución**:
```python
# Verificar en urls.py:
path('api/validate-sheet-rename/', views.validate_sheet_rename, ...),

# Verificar en views.py:
@require_http_methods(["POST"])
def validate_sheet_rename(request):
    ...

# Reiniciar servidor Django
```

---

### Error: CSRF token missing

**Síntoma**: 403 Forbidden en requests AJAX

**Solución**:
```javascript
// Verificar que getCookie() existe en el JS
function getCookie(name) { ... }

// Verificar header en fetch:
headers: {
    'X-CSRFToken': getCookie('csrftoken')
}
```

---

### Error: Tipos no se infieren

**Síntoma**: column_types vacío en template

**Solución**:
```python
# En views.py, verificar que se llama infer_sql_type():
from .utils.validators import infer_sql_type

for col in df.columns:
    type_info = infer_sql_type(df[col])
    column_types[str(col)] = type_info

# Verificar logs del servidor:
# Debe mostrar: "Hoja 'X': Y columnas, nombre sugerido: 'Z'"
```

---

## ✅ CHECKLIST DE VERIFICACIÓN

### Backend

- [ ] Servidor Django inicia sin errores
- [ ] No hay errores de import
- [ ] Migraciones aplicadas (`python manage.py showmigrations`)
- [ ] Endpoint `/api/validate-sheet-rename/` responde
- [ ] Endpoint `/api/excel/<id>/infer-types/` responde
- [ ] Redirect va directo a `/multi-config/` (no a `/sheets/`)

### Frontend

- [ ] JavaScript carga sin errores (sin errores en Console)
- [ ] Logs de inicialización aparecen en Console
- [ ] Función `validateSheetRename()` definida
- [ ] Función `inferColumnTypes()` definida
- [ ] Función `validateDefaultValue()` definida
- [ ] Función `updatePlaceholderForType()` definida

### Integración

- [ ] Al seleccionar columna, se muestra configuración
- [ ] Tipo SQL se sugiere automáticamente
- [ ] Placeholder cambia según tipo SQL
- [ ] Validación de default funciona
- [ ] Guardado de proceso funciona
- [ ] `type_configuration` se guarda en BD
- [ ] Normalización se ejecuta al procesar datos

---

## 📊 TESTING DE RENDIMIENTO

### Test de carga

```python
# Crear Excel con 100 columnas
import pandas as pd
import numpy as np

data = {f'col_{i}': np.random.randint(0, 100, 1000) for i in range(100)}
df = pd.DataFrame(data)
df.to_excel('test_100_cols.xlsx', index=False)

# Subir y cronometrar:
# - Tiempo de inferencia
# - Tiempo de carga de página
# - Tiempo de guardado
```

✅ **Esperado**:
- Inferencia: < 5 segundos
- Carga página: < 2 segundos
- Guardado: < 3 segundos

---

## 🎯 TESTS DE CASOS EXTREMOS

### Caso 1: Excel vacío
```
- Subir Excel sin datos (solo headers)
- ✅ Debe funcionar sin errores
- ✅ Inferencia: tipos basados en nombres de columna
```

### Caso 2: Nombres duplicados
```
- Renombrar 2 hojas al mismo nombre
- ✅ Validación debe marcar error: "Nombre duplicado"
```

### Caso 3: Caracteres especiales
```
- Nombres con: ñ, á, é, !, @, #, $, %, &
- ✅ Deben normalizarse correctamente
```

### Caso 4: Valores NULL masivos
```
- Columna con 90% de valores NULL
- ✅ Inferencia debe sugerir nullable=true
```

### Caso 5: Tipos mixtos
```
- Columna con números y texto
- ✅ Inferencia debe sugerir NVARCHAR con advertencia
```

---

## 📝 REPORTE DE BUGS

Si encuentras un bug, documéntalo así:

```markdown
### Bug: [Título descriptivo]

**Archivo**: [nombre del archivo]
**Línea**: [número de línea aproximado]

**Pasos para reproducir**:
1. [Paso 1]
2. [Paso 2]
3. [Paso 3]

**Comportamiento esperado**:
[Qué debería pasar]

**Comportamiento actual**:
[Qué pasa realmente]

**Logs/Errores**:
```
[Copiar error completo]
```

**Screenshot**:
[Si aplica]

**Posible solución**:
[Tu hipótesis]
```

---

## ✅ APROBACIÓN FINAL

Una vez completados TODOS los tests:

- [ ] ✅ Todos los tests rápidos pasados
- [ ] ✅ Todos los tests detallados pasados
- [ ] ✅ Casos extremos manejados
- [ ] ✅ Sin errores en consola
- [ ] ✅ Sin errores en logs del servidor
- [ ] ✅ Rendimiento aceptable

**Estado**: 🎉 **SISTEMA LISTO PARA PRODUCCIÓN**
