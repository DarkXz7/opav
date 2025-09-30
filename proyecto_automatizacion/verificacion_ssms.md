# Verificación de Datos en SQL Server Management Studio (SSMS)

## Pasos para verificar los datos insertados en SQL Server

### 1. Conectarse a SQL Server Management Studio

1. Abra SQL Server Management Studio (SSMS)
2. En la ventana de conexión, configure los siguientes parámetros:
   - **Tipo de servidor**: Database Engine
   - **Nombre del servidor**: `localhost\SQLEXPRESS` (o el nombre de su instancia)
   - **Autenticación**: Autenticación de SQL Server
   - **Inicio de sesión**: `miguel` (o el usuario configurado)
   - **Contraseña**: `16474791@` (o la contraseña configurada)
3. Haga clic en "Conectar"

### 2. Navegar a la base de datos y tabla

1. En el Explorador de objetos (panel izquierdo), expanda:
   - **Bases de datos**
   - **LogsAutomatizacion**
   - **Tablas**
2. Busque la tabla `ProcesoLog`

### 3. Consultar los datos de la tabla

1. Haga clic derecho en la tabla `ProcesoLog`
2. Seleccione "Seleccionar las primeras 1000 filas" o "Editar las primeras 200 filas"
   - Esto abrirá una ventana de consulta con los resultados

Alternativamente, puede ejecutar una consulta personalizada:

1. Haga clic en "Nueva Consulta" en la barra de herramientas
2. Asegúrese de que la base de datos `LogsAutomatizacion` esté seleccionada en el menú desplegable
3. Escriba y ejecute la siguiente consulta:

```sql
SELECT * FROM ProcesoLog
ORDER BY FechaEjecucion DESC;
```

### 4. Verificar los datos insertados

Los datos que debe ver incluyen:
- Un registro con la fecha de ejecución correspondiente al momento en que ejecutó el script
- Estado: "Completado"
- ParametrosEntrada: '{"fuente": "Test", "tipo": "Prueba"}'
- DuracionSegundos: 2.5

### 5. Solución de problemas

Si no ve los datos esperados:

1. **Verifique que la tabla existe**:
   ```sql
   SELECT * FROM INFORMATION_SCHEMA.TABLES 
   WHERE TABLE_NAME = 'ProcesoLog';
   ```

2. **Verifique la estructura de la tabla**:
   ```sql
   EXEC sp_help 'ProcesoLog';
   ```

3. **Verifique los permisos de usuario**:
   ```sql
   SELECT * FROM fn_my_permissions('ProcesoLog', 'OBJECT');
   ```

4. **Comprobar que se está usando la base de datos correcta**:
   ```sql
   SELECT DB_NAME() AS CurrentDatabase;
   ```

5. **Si necesita crear la tabla manualmente**:
   ```sql
   CREATE TABLE ProcesoLog (
       ProcesoID INT IDENTITY(1,1) PRIMARY KEY,
       FechaEjecucion DATETIME NOT NULL,
       Estado VARCHAR(100) NOT NULL,
       ParametrosEntrada NVARCHAR(MAX) NULL,
       DuracionSegundos FLOAT NULL,
       ErrorDetalle NVARCHAR(MAX) NULL
   );
   ```
