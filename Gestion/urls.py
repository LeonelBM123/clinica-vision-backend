from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'usuarios', views.UsuarioViewSet)
router.register(r'roles', views.RolViewSet)
router.register(r'medicos', views.MedicoViewSet)
router.register(r'especialidades', views.EspecialidadViewSet)
router.register(r'patologias', views.PatologiasOViewSet)
router.register(r'pacientes', views.PacienteViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
    path('api/bitacora/', views.BitacoraListAPIView.as_view(), name='bitacora-list')
]