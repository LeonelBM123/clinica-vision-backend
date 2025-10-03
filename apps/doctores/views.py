from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view
from rest_framework.response import Response
from rest_framework import generics
from rest_framework import permissions
from apps.acounts.utils import get_actor_usuario_from_request, log_action
from .models import *
from .serializers import *
from django.contrib.auth.models import User

class EspecialidadViewSet(viewsets.ModelViewSet):
    queryset = Especialidad.objects.all()
    serializer_class = EspecialidadSerializer
    
    # GET /api/especialidades/ - Lista todas las especialidades
    # POST /api/especialidades/ - Crea nueva especialidad
    # GET /api/especialidades/{id}/ - Obtiene una especialidad
    # PUT /api/especialidades/{id}/ - Actualiza especialidad completa
    # PATCH /api/especialidades/{id}/ - Actualiza parcialmente
    # DELETE /api/especialidades/{id}/ - Elimina especialidad

class MedicoViewSet(viewsets.ModelViewSet):
    queryset = Medico.objects.all()
    serializer_class = MedicoSerializer

    # Sobrescribir create (POST)
    def perform_create(self, serializer):
        medico = serializer.save()
        
        actor = get_actor_usuario_from_request(self.request)
        log_action(
            request=self.request,
            accion=f"Creó médico {medico.medico.nombre} (id:{medico.medico.pk})",
            objeto=f"Médico: {medico.medico.nombre} (id:{medico.medico.pk})",
            usuario=actor
        )

    # Sobrescribir update (PUT/PATCH)
    def perform_update(self, serializer):
        medico = serializer.save()
        actor = get_actor_usuario_from_request(self.request)
        log_action(
            request=self.request,
            accion=f"Actualizó médico {medico.medico.nombre} (id:{medico.medico.pk})",
            objeto=f"Médico: {medico.medico.nombre} (id:{medico.medico.pk})",
            usuario=actor
        )

    # Sobrescribir destroy (DELETE)
    def destroy(self, request, *args, **kwargs):
        medico_instance = self.get_object()
        usuario_a_eliminar = medico_instance.medico
        actor = get_actor_usuario_from_request(request)

        try:
            user_auth = User.objects.get(email=usuario_a_eliminar.correo)
            user_auth.delete()
        except User.DoesNotExist:
            pass
        
        # Log antes de eliminar
        log_action(
            request=request,
            accion=f"Eliminó médico {usuario_a_eliminar.nombre} (id:{usuario_a_eliminar.pk})",
            objeto=f"Médico: {usuario_a_eliminar.nombre} (id:{usuario_a_eliminar.pk})",
            usuario=actor
        )

        # Eliminar usuario y médico
        usuario_a_eliminar.delete()
        medico_instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    # GET /api/medicos/ - Lista todos los médicos
    # POST /api/medicos/ - Crea nuevo médico
    # GET /api/medicos/{id}/ - Obtiene un médico
    # PUT /api/medicos/{id}/ - Actualiza médico completo
    # PATCH /api/medicos/{id}/ - Actualiza parcialmente
    # DELETE /api/medicos/{id}/ - Elimina médico y su usuario asociado

class TipoAtencionViewSet(viewsets.ModelViewSet):#falta crear las ficniones para eliminar logicamente 
    queryset = Tipo_Atencion.objects.all()
    serializer_class = TipoAtencionSerializer

class BloqueHorarioViewSet(viewsets.ModelViewSet):#falta crear las ficniones para eliminar logicamente 
    queryset = Bloque_Horario.objects.all()
    serializer_class = BloqueHorarioSerializer