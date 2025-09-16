from django.db import models
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
    id = models.AutoField(primary_key=True)  # ID propio del paciente
    usuario = models.OneToOneField(
        Usuario,
        on_delete=models.SET_NULL,
        null=True,      # permite que el usuario se borre sin eliminar al paciente
        blank=True,
        related_name='paciente_profile'
    )
    numero_historia_clinica = models.CharField(
        max_length=64,
        unique=True,
        blank=False,
        null=False,
        verbose_name="Número de historia clínica"
    )
    
    alergias_medicamentos = models.TextField(
        blank=True,
        null=True,
        verbose_name="Alergias a medicamentos"
    )
    antecedentes_oculares = models.TextField(
        blank=False,
        null=False,
        verbose_name="Antecedentes oftalmológicos"
    )
    agudeza_visual_derecho = models.CharField(
        max_length=10,
        blank=False,
        null=False,
        verbose_name="Agudeza visual ojo derecho"
    )
    agudeza_visual_izquierdo = models.CharField(
        max_length=10,
        blank=False,
        null=False,
        verbose_name="Agudeza visual ojo izquierdo"
    )
    presion_intraocular_derecho = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        blank=False,
        null=False,
        verbose_name="Presión intraocular ojo derecho"
    )
    presion_intraocular_izquierdo = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        blank=False,
        null=False,
        verbose_name="Presión intraocular ojo izquierdo"
    )
    diagnostico_ocular = models.TextField(
        blank=True,
        null=True,
        verbose_name="Diagnóstico ocular"
    )
    estado = models.BooleanField(
        default=True,
        help_text="Activo = True, Eliminado = False"
    )
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_modificacion = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.paciente.nombre} - HC: {self.numero_historia_clinica}"

    class Meta:
        verbose_name = "Paciente"
        verbose_name_plural = "Pacientes"
        ordering = ['usuario__nombre']
        indexes = [
            models.Index(fields=['estado']),
            models.Index(fields=['numero_historia_clinica']),
        ]
