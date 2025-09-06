# views.py
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Usuario, Rol, Medico, Especialidad
from .serializers import UsuarioSerializer, RolSerializer, MedicoSerializer, EspecialidadSerializer
# viewsets.ModelViewSet automáticamente crea los CRUD endpoints:

class RolViewSet(viewsets.ModelViewSet):
    queryset = Rol.objects.all()
    serializer_class = RolSerializer
    
    # GET /api/roles/ - Lista todos los roles
    # POST /api/roles/ - Crea nuevo rol
    # GET /api/roles/{id}/ - Obtiene un rol
    # PUT /api/roles/{id}/ - Actualiza rol completo
    # PATCH /api/roles/{id}/ - Actualiza parcialmente
    # DELETE /api/roles/{id}/ - Elimina rol

class EspecialidadViewSet(viewsets.ModelViewSet):
    queryset = Especialidad.objects.all()
    serializer_class = EspecialidadSerializer
    
    # GET /api/especialidades/ - Lista todas las especialidades
    # POST /api/especialidades/ - Crea nueva especialidad
    # GET /api/especialidades/{id}/ - Obtiene una especialidad
    # PUT /api/especialidades/{id}/ - Actualiza especialidad completa
    # PATCH /api/especialidades/{id}/ - Actualiza parcialmente
    # DELETE /api/especialidades/{id}/ - Elimina especialidad

class UsuarioViewSet(viewsets.ModelViewSet):
    queryset = Usuario.objects.all()
    serializer_class = UsuarioSerializer
    
    # GET /api/usuarios/ - Lista todos los usuarios
    # POST /api/usuarios/ - Crea nuevo usuario
    # GET /api/usuarios/{id}/ - Obtiene un usuario
    # PUT /api/usuarios/{id}/ - Actualiza usuario completo
    # PATCH /api/usuarios/{id}/ - Actualiza parcialmente
    # DELETE /api/usuarios/{id}/ - Elimina usuario
    
    @action(detail=True, methods=['post'])
    def cambiar_password(self, request, pk=None):
        # Endpoint especial para cambiar contraseña
        usuario = self.get_object()
        nuevo_password = request.data.get('password')

        if not nuevo_password:
            return Response(
                {'error': 'La contraseña es requerida'},
                status=status.HTTP_400_BAD_REQUEST
            )

        usuario.set_password(nuevo_password)
        usuario.save()
        return Response({'message': 'Contraseña actualizada correctamente'}, status=status.HTTP_200_OK)

class MedicoViewSet(viewsets.ModelViewSet):
    queryset = Medico.objects.all()
    serializer_class = MedicoSerializer
    
    # GET /api/medicos/ - Lista todos los médicos
    # POST /api/medicos/ - Crea nuevo médico
    # GET /api/medicos/{id}/ - Obtiene un médico
    # PUT /api/medicos/{id}/ - Actualiza médico completo
    # PATCH /api/medicos/{id}/ - Actualiza parcialmente
    # DELETE /api/medicos/{id}/ - Elimina médico