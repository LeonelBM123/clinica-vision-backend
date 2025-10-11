from rest_framework import serializers
from .models import *

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