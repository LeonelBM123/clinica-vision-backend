from django.db import models
from apps.acounts.models import Usuario
from apps.doctores.models import Bloque_Horario
class PatologiasO(models.Model):
    
    gravedad_opciones = [
        ('LEVE', 'Leve'),
        ('MODERADA', 'Moderada'),
        ('GRAVE', 'Grave'),
        ('CRITICA', 'Critica'),    
    ]
    
    nombre = models.CharField(
        max_length=120,
        unique=True,
        help_text="Nombre oficial de la patología") 
    
    alias = models.CharField(
        max_length=120,
        blank=True,
        help_text="Alias o nombres comunes de la patología",)
    
    descripcion = models.TextField(
        blank=True,
        help_text="Descripción de la patología")
    
    gravedad = models.CharField(
        max_length=50,
        choices=gravedad_opciones)
    
    estado = models.BooleanField(
        default=True,
        help_text= "Activo = True, Eliminado = False")
    
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_modificacion = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Patologia"
        verbose_name_plural = "Patologias"
        ordering = ['nombre']
        indexes = [
            models.Index(fields=['nombre']),
            models.Index(fields=['gravedad']),
        ]
    
    def __str__(self):
        return self.nombre
    
class Paciente(models.Model):
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE)
    numero_historia_clinica = models.CharField(max_length=64, unique=True,help_text="Ejemplo: HC-2023-0001")
    patologias = models.ManyToManyField('PatologiasO', related_name='pacientes', blank=True)
    agudeza_visual_derecho = models.CharField(max_length=20, blank=True,help_text="Ejemplo: 20/20")
    agudeza_visual_izquierdo = models.CharField(max_length=20, blank=True,help_text="Ejemplo: 20/20")
    presion_ocular_derecho = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True,help_text="Ejemplo: 15.50")
    presion_ocular_izquierdo = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True,help_text="Ejemplo: 15.50")
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_modificacion = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['usuario']

    def __str__(self):
        return f" {self.usuario.nombre} - {self.numero_historia_clinica}"

#tablas creadas para manejar las citas medicas
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