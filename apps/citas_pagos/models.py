from django.db import models
from apps.historiasDiagnosticos.models import Paciente
from apps.doctores.models import Bloque_Horario
class Cita_Medica(models.Model):

    fecha = models.DateField(help_text="Fecha de la cita médica")
    hora_inicio = models.TimeField(help_text="Hora de inicio de la cita médica")
    hora_fin = models.TimeField(help_text="Hora de fin de la cita médica")
    estado = models.BooleanField(default=True, help_text="Activo = True, Cancelado = False")
    notas = models.TextField(blank=True, help_text="Notas adicionales sobre la cita médica")
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_modificacion = models.DateTimeField(auto_now=True)
    motivo_cancelacion = models.TextField(blank=True, help_text="Motivo de la cancelación, si aplica ")
  
    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE, related_name='citas')
    bloque_horario = models.ForeignKey(Bloque_Horario, on_delete=models.CASCADE, related_name='citas')
    class Meta:
        verbose_name = "Cita Médica"
        verbose_name_plural = "Citas Médicas"
        ordering = ['-fecha_creacion']
        indexes = [
            models.Index(fields=['fecha_creacion']),
            models.Index(fields=['estado']),
        ]    