from rest_framework import serializers
from .models import *

class PatologiasOSerializer(serializers.ModelSerializer):
    class Meta:
        model = PatologiasO
        fields = '__all__'


class PacienteSerializer(serializers.ModelSerializer):
    usuario = serializers.PrimaryKeyRelatedField(
        queryset=Usuario.objects.filter(rol__nombre='PACIENTE')
    )
    nombre = serializers.CharField(source='usuario.nombre', read_only=True)
    correo = serializers.CharField(source='usuario.correo', read_only=True)
    fecha_nacimiento = serializers.DateField(source='usuario.fecha_nacimiento', read_only=True)
    patologias = serializers.PrimaryKeyRelatedField(
        queryset=PatologiasO.objects.all(),
        many=True,
        required=False,
    )
    class Meta:
        model = Paciente
        fields = [
            'id',
            'usuario',
            'nombre',
            'correo',
            'fecha_nacimiento',
            'numero_historia_clinica',
            'patologias',
            'agudeza_visual_derecho',
            'agudeza_visual_izquierdo',
            'presion_ocular_derecho',
            'presion_ocular_izquierdo',
            'fecha_creacion',
            'fecha_modificacion',
        ]
        
class CitaMedicaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cita_Medica
        fields = ['id',
                  'paciente',
                  'bloque_horario', 
                  'fecha', 
                  'hora_inicio',
                  'hora_fin',  
                  'motivo_cancelacion', 
                  'notas', 
                  'fecha_creacion', 
                  'fecha_modificacion']