from rest_framework import serializers
from django.contrib.auth.hashers import make_password
from .models import *
from apps.acounts.models import Usuario, Rol

class EspecialidadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Especialidad
        fields = '__all__'

class MedicoSerializer(serializers.ModelSerializer):

    # Campos para crear usuario nuevo
    nombre_usuario = serializers.CharField(write_only=True, required=False)
    correo_usuario = serializers.EmailField(write_only=True, required=False)
    password_usuario = serializers.CharField(write_only=True, required=False)
    sexo_usuario = serializers.CharField(write_only=True, required=False)
    fecha_nacimiento_usuario = serializers.DateField(write_only=True, required=False)
    telefono_usuario = serializers.CharField(write_only=True, required=False, allow_blank=True)
    direccion_usuario = serializers.CharField(write_only=True, required=False, allow_blank=True)
    
    # Info del médico para lectura
    info_medico = serializers.SerializerMethodField(read_only=True)
    especialidades_nombres = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Medico
        fields = [
            'medico', 
            'numero_colegiado', 
            'especialidades',
            'nombre_usuario', 'correo_usuario', 'password_usuario',
            'sexo_usuario', 'fecha_nacimiento_usuario', 
            'telefono_usuario', 'direccion_usuario',
            'info_medico', 'especialidades_nombres'
        ]
        extra_kwargs = {
            'medico': {'required': False}
        }
    
    def get_info_medico(self, obj):
        if obj.medico:
            return {
                'id': obj.medico.id,
                'nombre': obj.medico.nombre,
                'correo': obj.medico.correo,
                'sexo': obj.medico.sexo,
                'fecha_nacimiento': obj.medico.fecha_nacimiento,
                'telefono': obj.medico.telefono,
                'direccion': obj.medico.direccion,
                'rol': obj.medico.rol.nombre if obj.medico.rol else None
            }
        return None
    
    def get_especialidades_nombres(self, obj):
        return [esp.nombre for esp in obj.especialidades.all()]

    def create(self, validated_data):
        # Extraer datos de usuario si se proporcionan
        usuario_data = {}
        usuario_fields = [
            'nombre_usuario', 'correo_usuario', 'password_usuario',
            'sexo_usuario', 'fecha_nacimiento_usuario', 
            'telefono_usuario', 'direccion_usuario'
        ]
        
        for field in usuario_fields:
            if field in validated_data:
                field_name = field.replace('_usuario', '')
                usuario_data[field_name] = validated_data.pop(field)
        
        # Extraer especialidades 
        especialidades_data = validated_data.pop('especialidades', [])

        try:
            rol_medico = Rol.objects.get(nombre='MÉDICO')
        except Rol.DoesNotExist:
            raise serializers.ValidationError("El rol MÉDICO no existe. Crearlo primero.")
        
        # Si se proporcionaron datos de usuario, crearlo
        if usuario_data:
            usuario_data['rol'] = rol_medico
            
            if 'password' in usuario_data:
                usuario_data['password'] = make_password(usuario_data['password'])
            
            usuario = Usuario.objects.create(**usuario_data)
            validated_data['medico'] = usuario
        
        elif 'medico' in validated_data:
            usuario_existente = validated_data['medico']
            # ACTUALIZAR el rol del usuario existente a MÉDICO
            usuario_existente.rol = rol_medico
            usuario_existente.save()
        else:
            raise serializers.ValidationError({
                "medico": "Se requiere un usuario (existente o nuevo)"
            })
        
        # Crear el médico primero
        medico = Medico.objects.create(**validated_data)
        
        # Agregar especialidades
        if especialidades_data:
            medico.especialidades.set(especialidades_data)
        
        return medico
    
class TipoAtencionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tipo_Atencion
        fields = '__all__'

class BloqueHorarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bloque_Horario
        fields = '__all__'    