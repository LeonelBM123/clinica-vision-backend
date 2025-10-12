from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view
from rest_framework.response import Response
from rest_framework import generics
from rest_framework import permissions
from apps.cuentas.utils import get_actor_usuario_from_request, log_action
from .models import *
from .serializers import *
from django.contrib.auth.models import User

class MultiTenantMixin:
    """Mixin para filtrar datos por grupo del usuario actual"""
    
    permission_classes = [permissions.IsAuthenticated]  # Requiere autenticación
    
    def get_user_grupo(self):
        """Obtiene el grupo del usuario actual"""
        if hasattr(self.request, 'user') and self.request.user.is_authenticated:
            try:
                usuario = Usuario.objects.get(correo=self.request.user.email)
                return usuario.grupo
            except Usuario.DoesNotExist:
                pass
        return None
    
    def is_super_admin(self):
        """Verifica si el usuario actual es super admin"""
        if hasattr(self.request, 'user') and self.request.user.is_authenticated:
            try:
                usuario = Usuario.objects.get(correo=self.request.user.email)
                return usuario.rol and usuario.rol.nombre == 'superAdmin'
            except Usuario.DoesNotExist:
                pass
        return False
    
    def filter_by_grupo(self, queryset):
        """Filtra el queryset por el grupo del usuario actual"""
        if self.is_super_admin():
            return queryset  # Super admin ve todo
        
        grupo = self.get_user_grupo()
        if grupo:
            # Verifica si el modelo tiene campo grupo (incluyendo herencia)
            model = queryset.model
            has_grupo_field = any(
                hasattr(field, 'name') and field.name == 'grupo' 
                for field in model._meta.get_fields()
            )
            
            if has_grupo_field:
                print(f"🔍 Filtering {model.__name__} by grupo: {grupo}")
                return queryset.filter(grupo=grupo)
        
        print(f"🔍 No filtering applied for {queryset.model.__name__}")
        return queryset

class EspecialidadViewSet(viewsets.ModelViewSet):
    queryset = Especialidad.objects.all()
    serializer_class = EspecialidadSerializer

class MedicoViewSet(MultiTenantMixin, viewsets.ModelViewSet):  
    queryset = Medico.objects.all()
    serializer_class = MedicoSerializer
    
    def get_queryset(self):
        queryset = Medico.objects.all()
        # Usar el filtrado por grupo del Mixin
        queryset = self.filter_by_grupo(queryset)
        
        # Por defecto, solo médicos activos
        if self.action == 'list':
            return queryset.filter(estado=True)
        return queryset

    def create(self, request, *args, **kwargs):
        """Override create para debug"""
        print("🔍 === CREATE MÉDICO ===")
        print(f"🔍 User: {request.user}")
        print(f"🔍 Authenticated: {request.user.is_authenticated}")
        print(f"🔍 Data: {request.data}")
        
        try:
            return super().create(request, *args, **kwargs)
        except Exception as e:
            print(f"❌ Error en create: {e}")
            import traceback
            traceback.print_exc()
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_400_BAD_REQUEST
            )

    def perform_create(self, serializer):
        # Asignar automáticamente el grupo del usuario que crea
        try:
            usuario = Usuario.objects.get(correo=self.request.user.email)
            print(f"🔍 Usuario creador: {usuario}, Grupo: {usuario.grupo}")
            
            # ASIGNAR ROL MÉDICO AUTOMÁTICAMENTE
            try:
                rol_medico = Rol.objects.get(nombre='medico')
            except Rol.DoesNotExist:
                # Si no existe, buscar por ID 4 o crear uno
                try:
                    rol_medico = Rol.objects.get(id=4)
                except Rol.DoesNotExist:
                    # Crear rol médico si no existe
                    rol_medico = Rol.objects.create(
                        nombre='medico',
                        descripcion='Médico del sistema'
                    )
            
            print(f"🔍 Rol asignado: {rol_medico.nombre} (ID: {rol_medico.id})")
            
            # OBTENER Y HASHEAR LA CONTRASEÑA
            validated_data = serializer.validated_data
            password = validated_data.get('password')
            
            if password:
                from django.contrib.auth.hashers import make_password
                validated_data['password'] = make_password(password)
                print("🔍 Contraseña hasheada")
            
            # Crear también el User de Django
            correo = validated_data.get('correo')
            if correo and password:
                try:
                    User.objects.create_user(
                        username=correo,
                        email=correo,
                        password=password  # Django ya la hashea automáticamente
                    )
                    print("🔍 User de Django creado")
                except Exception as e:
                    print(f"⚠️ Error creando User Django: {e}")
            
            # Guardar con grupo Y rol
            medico = serializer.save(grupo=usuario.grupo, rol=rol_medico)
            
            # Log de la acción
            actor = get_actor_usuario_from_request(self.request)
            log_action(
                request=self.request,
                accion=f"Creó el médico {medico.nombre} (id:{medico.id})",
                objeto=f"Médico: {medico.nombre} (id:{medico.id})",
                usuario=actor
            )
            print(f"✅ Médico creado: {medico}")
            
        except Usuario.DoesNotExist:
            print("❌ Usuario no encontrado")
            # Fallback con rol médico
            grupo = Grupo.objects.first()
            try:
                rol_medico = Rol.objects.get(nombre='medico')
            except Rol.DoesNotExist:
                rol_medico = Rol.objects.get(id=4)
            
            # Hashear contraseña en fallback también
            validated_data = serializer.validated_data
            password = validated_data.get('password')
            if password:
                from django.contrib.auth.hashers import make_password
                validated_data['password'] = make_password(password)
                
            medico = serializer.save(grupo=grupo, rol=rol_medico)
            print(f"✅ Médico creado con grupo fallback y rol médico")

    def perform_update(self, serializer):
        medico = serializer.save()
        
        # Log de la acción
        actor = get_actor_usuario_from_request(self.request)
        log_action(
            request=self.request,
            accion=f"Actualizó el médico {medico.nombre} (id:{medico.id})",
            objeto=f"Médico: {medico.nombre} (id:{medico.id})",
            usuario=actor
        )

    def perform_destroy(self, instance):
        # Soft delete: solo cambia estado a False
        nombre = instance.nombre
        pk = instance.pk
        instance.estado = False
        instance.save()
        
        # Log de la acción
        actor = get_actor_usuario_from_request(self.request)
        log_action(
            request=self.request,
            accion=f"Eliminó (soft delete) el médico {nombre} (id:{pk})",
            objeto=f"Médico: {nombre} (id:{pk})",
            usuario=actor
        )
    
    @action(detail=False, methods=['get'])
    def eliminados(self, request):
        queryset = Medico.objects.all()
        queryset = self.filter_by_grupo(queryset)  # Filtrar por grupo
        eliminados = queryset.filter(estado=False)
        serializer = self.get_serializer(eliminados, many=True)
        return Response(serializer.data)    
    
    @action(detail=True, methods=['post'])
    def restaurar(self, request, pk=None):
        medico = self.get_object()
        medico.estado = True
        medico.save()
        
        # Log de la acción
        actor = get_actor_usuario_from_request(self.request)
        log_action(
            request=self.request,
            accion=f"Restauró el médico {medico.nombre} (id:{medico.id})",
            objeto=f"Médico: {medico.nombre} (id:{medico.id})",
            usuario=actor
        )
        
        serializer = self.get_serializer(medico)
        return Response(serializer.data, status=status.HTTP_200_OK)

class TipoAtencionViewSet(MultiTenantMixin, viewsets.ModelViewSet):
    queryset = Tipo_Atencion.objects.all()
    serializer_class = TipoAtencionSerializer
    
    def get_queryset(self):
        queryset = Tipo_Atencion.objects.all()
        return self.filter_by_grupo(queryset)

class BloqueHorarioViewSet(MultiTenantMixin, viewsets.ModelViewSet):
    queryset = Bloque_Horario.objects.all()
    serializer_class = BloqueHorarioSerializer
    
    def get_queryset(self):
        queryset = Bloque_Horario.objects.all()
        return self.filter_by_grupo(queryset)