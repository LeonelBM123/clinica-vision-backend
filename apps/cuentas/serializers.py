from rest_framework import serializers
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from .models import *

class RolSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rol
        fields = '__all__'

class UsuarioSerializer(serializers.ModelSerializer):
    # Mostrar el nombre del rol en lugar de solo el ID
    rol_nombre = serializers.CharField(source='rol.nombre', read_only=True)
    
    class Meta:
        model = Usuario
        fields = '__all__'
        extra_kwargs = {'password': {'write_only': True}}
    
    def create(self, validated_data):
        password = validated_data.pop('password', None)
        # Hashear la contraseña antes de crear el usuario
        if password:
            validated_data['password'] = make_password(password)
        usuario = Usuario.objects.create(**validated_data)
        return usuario
    
    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        # Hashear la contraseña si se proporciona
        if password:
            validated_data['password'] = make_password(password)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance

class BitacoraSerializer(serializers.ModelSerializer):
    usuario = serializers.SerializerMethodField()

    class Meta:
        model = Bitacora
        fields = ['id', 'usuario', 'accion', 'ip', 'objeto', 'extra', 'timestamp']

    def get_usuario(self, obj):
        # adapta según tu modelo Usuario: mostramos el nombre
        return obj.usuario.nombre if obj.usuario else None