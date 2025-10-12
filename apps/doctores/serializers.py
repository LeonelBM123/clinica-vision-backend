from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from django.db import transaction
from .models import *
from apps.cuentas.models import Usuario, Rol

class EspecialidadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Especialidad
        fields = '__all__'

class MedicoSerializer(serializers.ModelSerializer):
    rol_nombre = serializers.CharField(source='rol.nombre', read_only=True)
    grupo_nombre = serializers.CharField(source='grupo.nombre', read_only=True)
    puede_acceder = serializers.SerializerMethodField()
    especialidades_nombres = serializers.SerializerMethodField()
    especialidades = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Especialidad.objects.all(),
        required=False
    )
    
    class Meta:
        model = Medico
        fields = '__all__'
        extra_kwargs = {
            'password': {'write_only': True},
            # REMUEVE 'grupo': {'required': True} - Ahora se asigna automáticamente
        }
    
    def get_puede_acceder(self, obj):
        return obj.puede_acceder_sistema()
    
    def get_especialidades_nombres(self, obj):
        return [esp.nombre for esp in obj.especialidades.all()]
    
    def update(self, instance, validated_data):
        # Extraer especialidades antes de actualizar
        especialidades_data = validated_data.pop('especialidades', None)
        
        # Hashear la contraseña si se proporciona
        password = validated_data.pop('password', None)
        if password:
            from django.contrib.auth.hashers import make_password
            validated_data['password'] = make_password(password)
        
        # Actualizar campos normales
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        instance.save()
        
        # Actualizar especialidades si se proporcionaron
        if especialidades_data is not None:
            instance.especialidades.set(especialidades_data)
        
        return instance
    
class TipoAtencionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tipo_Atencion
        fields = '__all__'

class BloqueHorarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bloque_Horario
        fields = '__all__'    