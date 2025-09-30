from django.db import models

class ProcesoLog(models.Model):
    """
    Modelo para almacenar registros de logs de procesos en SQL Server Express
    Mapea a la tabla existente 'ProcesoLog' en la base de datos 'LogsAutomatizacion'
    """
    LogID = models.AutoField(primary_key=True)
    ProcesoID = models.CharField(max_length=36, null=True, blank=True)  # UUID como string
    NombreProceso = models.CharField(max_length=255, null=True, blank=True)  # Coincide con SQL Server
    FechaEjecucion = models.DateTimeField()
    Estado = models.CharField(max_length=20)  # Coincide con SQL Server (varchar(20))
    ParametrosEntrada = models.TextField(null=True, blank=True)
    DuracionSegundos = models.IntegerField(null=True, blank=True)  # INT en SQL Server
    MensajeError = models.TextField(null=True, blank=True)
    
    class Meta:
        managed = False  # Django no gestiona esta tabla (ya existe)
        db_table = 'ProcesoLog'  # Nombre exacto de la tabla en SQL Server
        app_label = 'automatizacion'
        verbose_name = 'Log de Proceso'
        verbose_name_plural = 'Logs de Procesos'
    
    def __str__(self):
        return f"Proceso {self.ProcesoID}: {self.Estado} ({self.FechaEjecucion})"
