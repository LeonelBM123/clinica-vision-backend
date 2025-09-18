from django.db import models
from django.conf import settings
from django.contrib.auth.hashers import make_password, check_password
from django.core.validators import MinLengthValidator

# Modelo de Rol
class Rol(models.Model):
    tipo_rol_opciones = [
        ('PACIENTE', 'Paciente'),
        ('MÉDICO', 'Médico'),
        ('ADMIN', 'Administrador'),
        ('RECEPCIONISTA', 'Recepcionista'),
    ]

    nombre = models.CharField(
        max_length=64,
        unique=True,
        verbose_name="Nombre del rol",
        choices=tipo_rol_opciones
    )

    def __str__(self):
        return self.get_nombre_display()

    class Meta:
        verbose_name = "Rol"
        verbose_name_plural = "Roles"
        ordering = ['nombre']

# Modelo de Usuario maestro
class Usuario(models.Model):  
    sexo_opciones = [
        ('M', 'Masculino'),
        ('F', 'Femenino'),
    ]

    nombre = models.CharField(
        max_length=128,
        verbose_name="Nombre completo"
    )
    
    password = models.CharField(max_length=128)
    
    correo = models.EmailField(
        unique=True,
        verbose_name="Correo electrónico"
    )
    
    sexo = models.CharField(
        max_length=1, 
        choices=sexo_opciones,
        verbose_name="Género"
    )
    
    fecha_nacimiento = models.DateField(
        verbose_name="Fecha de nacimiento"
    )
    
    telefono = models.CharField(
        max_length=8,
        blank=True,
        null=True,
        validators=[MinLengthValidator(8)],
        verbose_name="Teléfono"
    )
    
    direccion = models.CharField(
        max_length=256,
        blank=True,
        null=True,
        verbose_name="Dirección"
    )
    
    fecha_registro = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Fecha de registro"
    )
    
    estado = models.BooleanField(
        default=True,
        verbose_name="¿Está activo?"
    )
    
    ultimo_login = models.DateTimeField(
        auto_now=True,
        verbose_name="Último ingreso"
    )
    
    rol = models.ForeignKey(
        Rol, 
        on_delete=models.PROTECT,
        verbose_name="Rol del usuario",
        related_name='usuarios',
        null=True,
        blank=True
    )

    def set_password(self, raw_password):
        self.password = make_password(raw_password)
        self.save()
    
    def check_password(self, raw_password):
        return check_password(raw_password, self.password)
    
    def __str__(self):
        return f"{self.nombre} ({getattr(self.rol, 'nombre', 'Sin rol')})"

    class Meta:
        verbose_name = "Usuario del sistema"
        verbose_name_plural = "Usuarios del sistema"
        ordering = ['-fecha_registro']
        indexes = [
            models.Index(fields=['correo']),
            models.Index(fields=['rol', 'estado']),
        ]

# Modelo Especialidad
class Especialidad(models.Model):
    nombre = models.CharField(
        max_length=128,
        unique=True,
        verbose_name="Nombre de la especialidad"
    )

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = "Especialidad"
        verbose_name_plural = "Especialidades"
        ordering = ['nombre']

# Modelo de Medico
class Medico(models.Model):
    medico = models.OneToOneField(
        Usuario, 
        on_delete=models.CASCADE,
        primary_key=True,
        related_name='medico_profile'
    )
    numero_colegiado = models.CharField(
        max_length=64, 
        unique=True,
        verbose_name="Número de colegiado"
    )
    especialidades = models.ManyToManyField(
        Especialidad,
        related_name='medicos',
        verbose_name="Especialidades médicas",
        blank=True,
    )

    def __str__(self):
        return f"Dr. {self.medico.nombre} - {self.numero_colegiado}"

    class Meta:
        verbose_name = "Médico"
        verbose_name_plural = "Médicos"
        ordering = ['medico__nombre']

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
    numero_historia_clinica = models.CharField(max_length=64, unique=True)
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    fecha_nacimiento = models.DateField(null=True, blank=True)
    alergias = models.TextField(blank=True)
    antecedentes_oculares = models.TextField(blank=True)
    estado = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_modificacion = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.nombre} {self.apellido} ({self.numero_historia_clinica})"


class ExamenOcular(models.Model):
    paciente = models.ForeignKey(Paciente, related_name='examenes', on_delete=models.CASCADE)
    # Agudeza visual
    agudeza_visual_derecho = models.TextField( blank=True)
    agudeza_visual_izquierdo = models.TextField(blank=True)    
    # Presión intraocular
    presion_intraocular_derecho = models.FloatField(null=True, blank=True)
    presion_intraocular_izquierdo = models.FloatField(null=True, blank=True)
    # Diagnóstico
    diagnostico_ocular = models.TextField(blank=True)
    fecha = models.DateField(auto_now_add=True)  # Fecha del examen
    def __str__(self):
        return f"Examen {self.id} - {self.paciente.numero_historia_clinica}"

class Bitacora(models.Model):
    usuario = models.ForeignKey(
        Usuario,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='bitacoras'
    )
    accion = models.TextField(
        help_text="Descripción legible de la acción (ej: 'médico Pedro eliminó al paciente Juanito')"
    )
    ip = models.GenericIPAddressField(null=True, blank=True)
    objeto = models.CharField(
        max_length=200,
        null=True,
        blank=True,
        help_text="Texto corto indicando el objeto afectado (ej: 'Paciente: Juanito (id:4)')"
    )
    extra = models.JSONField(
        null=True,
        blank=True,
        help_text="Información adicional en JSON (opcional)"
    )
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ['-timestamp']
        verbose_name = 'Registro de bitácora'
        verbose_name_plural = 'Bitácoras'

    def str(self):
        user = self.usuario.nombre if self.usuario else "Anónimo"
        return f"{self.timestamp.isoformat()} — {user} — {self.accion[:80]}"