from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'usuarios', views.UsuarioViewSet)
router.register(r'roles', views.RolViewSet)
router.register(r'bitacoras', views.BitacoraViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('bitacora/', views.BitacoraListAPIView.as_view(), name='bitacora-list')
]