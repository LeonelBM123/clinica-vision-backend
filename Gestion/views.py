# views.py
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view
from rest_framework.response import Response
from .models import *
from .serializers import *
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
from rest_framework.permissions import IsAuthenticated,AllowAny
from rest_framework.decorators import permission_classes
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

    def perform_create(self, serializer):
        """
        Crea un User cada vez que se crea un Usuario, sin asociarlo.
        """
        data = serializer.validated_data

        # Crear el User de Django (para login/tokens)
        User.objects.create_user(

            username=data["correo"],  # usar correo como username
            email=data["correo"],
            password=data["password"]  # recibir password del request
        )
        # Guardar el Usuario normalmente
        serializer.save()

    @action(detail=False, methods=['post'])
    def login(self, request):
        correo = request.data.get('correo')
        password = request.data.get('password')
        if not correo or not password:
            return Response(
                {"error": "Correo y password son requeridos"},
                status=status.HTTP_400_BAD_REQUEST
            )
        # Buscar usuario en el modelo User usando el email
        user = get_object_or_404(User, email=correo)
        # Validar contraseña
        if not user.check_password(password):
            return Response(
                {"error": "Contraseña incorrecta"},
                status=status.HTTP_400_BAD_REQUEST
            )
        # Obtener o crear token
        token, created = Token.objects.get_or_create(user=user)

        # Si quieres, puedes incluir info del perfil extendido
        usuario_perfil = get_object_or_404(Usuario, correo=correo)

        return Response(
            {
                "message": "Login exitoso",
                "usuario_id": usuario_perfil.id if usuario_perfil else None,
                "token": token.key,
                "rol": usuario_perfil.rol.get_nombre_display() if usuario_perfil and usuario_perfil.rol else None
            },
            status=status.HTTP_200_OK
        )
    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def logout(self, request):
        return Response({"message": "Cierre de sesion exitoso"}, status=status.HTTP_200_OK)
            

class MedicoViewSet(viewsets.ModelViewSet):
    queryset = Medico.objects.all()
    serializer_class = MedicoSerializer
    
    # GET /api/medicos/ - Lista todos los médicos
    # POST /api/medicos/ - Crea nuevo médico
    # GET /api/medicos/{id}/ - Obtiene un médico
    # PUT /api/medicos/{id}/ - Actualiza médico completo
    # PATCH /api/medicos/{id}/ - Actualiza parcialmente
    # DELETE /api/medicos/{id}/ - Elimina médico


class PatologiasOViewSet(viewsets.ModelViewSet):
    queryset = PatologiasO.objects.all()  
    serializer_class = PatologiasOSerializer

    def get_queryset(self):
        # Por defecto, solo activos
        if self.action == 'list':
            return PatologiasO.objects.filter(estado=True)
        return PatologiasO.objects.all()

    def perform_destroy(self, instance):
        # Soft delete: solo cambia estado a False y actualiza fecha_modificacion
        instance.estado = False
        instance.save()
    
    @action(detail=False, methods=['get'])
    def eliminadas(self, request):
        eliminadas = PatologiasO.objects.filter(estado=False)
        serializer = self.get_serializer(eliminadas, many=True)
        return Response(serializer.data)    
    
    @action(detail=True, methods=['post'])
    def restaurar(self, request, pk=None):
        patologia = self.get_object()
        patologia.estado = True
        patologia.save()
        serializer = self.get_serializer(patologia)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    # GET /api/patologias/ (listar)
    # POST /api/patologias/ (crear)
    # GET /api/patologias/{id}/ (detalle)
    # PUT/PATCH /api/patologias/{id}/ (editar)
    # DELETE /api/patologias/{id}/ (soft delete)
    # GET /api/patologias/eliminadas/ (listar eliminadas)



class PacienteViewSet(viewsets.ModelViewSet):
    queryset = Paciente.objects.all()
    serializer_class = PacienteSerializer

    def get_queryset(self):
        # Por defecto, solo pacientes activos
        if self.action == 'list':
            return Paciente.objects.filter(estado=True)
        return Paciente.objects.all()

    def perform_destroy(self, instance):
        # Soft delete: solo cambiar estado a False
        instance.estado = False
        instance.save()

    @action(detail=False, methods=['get'])
    def eliminados(self, request):
        eliminados = Paciente.objects.filter(estado=False)
        serializer = self.get_serializer(eliminados, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def restaurar(self, request, pk=None):
        paciente = self.get_object()
        paciente.estado = True
        paciente.save()
        serializer = self.get_serializer(paciente)
        return Response(serializer.data, status=status.HTTP_200_OK)

def create(self, request, *args, **kwargs):
    examenes_data = request.data.pop('examenes', None)  # 👈 usa el related_name
    paciente_serializer = self.get_serializer(data=request.data)
    paciente_serializer.is_valid(raise_exception=True)
    paciente = paciente_serializer.save(estado=True)

    # Guardar exámenes asociados
    if examenes_data:
        if isinstance(examenes_data, dict):
            # Si mandas un solo examen
            examenes_data = [examenes_data]

        for examen_data in examenes_data:
            examen_data['paciente'] = paciente.id
            examen_serializer = ExamenOcularSerializer(data=examen_data)
            examen_serializer.is_valid(raise_exception=True)
            examen_serializer.save()

    headers = self.get_success_headers(paciente_serializer.data)
    return Response(paciente_serializer.data, status=status.HTTP_201_CREATED, headers=headers)


