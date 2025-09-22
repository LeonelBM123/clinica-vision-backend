# views.py
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view
from rest_framework.response import Response
from rest_framework import generics
from rest_framework import permissions
from Gestion.utils import get_actor_usuario_from_request, log_action
from .models import *
from .serializers import *
# from .models import Usuario, Rol, Medico, Especialidad
# from .serializers import UsuarioSerializer, RolSerializer, MedicoSerializer, EspecialidadSerializer
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

        usuario_obj = serializer.save()
        actor = get_actor_usuario_from_request(self.request)
        log_action(
            request=self.request,
            accion=f"Creó usuario {usuario_obj.nombre} (id:{usuario_obj.id})",
            objeto=f"Usuario: {usuario_obj.nombre} (id:{usuario_obj.id})",
            usuario=actor
        )

    def perform_destroy(self, instance):
        nombre = instance.nombre
        pk = instance.pk
        actor = get_actor_usuario_from_request(self.request)
        instance.delete()
        log_action(
            request=self.request,
            accion=f"Eliminó usuario {nombre} (id:{pk})",
            objeto=f"Usuario: {nombre} (id:{pk})",
            usuario=actor
        )

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
        actor = get_actor_usuario_from_request(request)
        log_action(
            request=request,
            accion=f"Inicio de sesión del usuario {usuario_perfil.nombre} (id:{usuario_perfil.id})",
            objeto=f"Usuario: {usuario_perfil.nombre} (id:{usuario_perfil.id})",
            usuario=actor
        )
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
    headers = self.get_success_headers(paciente_serializer.data)
    return Response(paciente_serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class BitacoraListAPIView(generics.ListAPIView):
    permission_classes = [permissions.IsAdminUser]  # solo admins por seguridad
    serializer_class = BitacoraSerializer
    pagination_class = None  # puedes habilitar paginación si quieres

    def get_queryset(self):
        qs = Bitacora.objects.all()
        start = self.request.query_params.get('start')  # YYYY-MM-DD
        end = self.request.query_params.get('end')      # YYYY-MM-DD
        usuario = self.request.query_params.get('usuario')
        if start:
            sd = parse_date(start)
            if sd:
                qs = qs.filter(timestampdategte=sd)
        if end:
            ed = parse_date(end)
            if ed:
                qs = qs.filter(timestampdatelte=ed)
        if usuario:
            # filtra por id o por nombre parcial
            if usuario.isdigit():
                qs = qs.filter(usuarioid=int(usuario))
            else:
                qs = qs.filter(usuarionombre__icontains=usuario)
        return qs
    
class BitacoraViewSet(viewsets.ModelViewSet):
    queryset = Bitacora.objects.all()
    serializer_class = BitacoraSerializer

# GET /api/roles/ - Lista todos los roles
# POST /api/roles/ - Crea nuevo rol
# GET /api/roles/{id}/ - Obtiene un rol
# PUT /api/roles/{id}/ - Actualiza rol completo
# PATCH /api/roles/{id}/ - Actualiza parcialmente
# DELETE /api/roles/{id}/ - Elimina rol