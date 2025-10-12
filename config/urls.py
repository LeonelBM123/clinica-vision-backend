from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponse

urlpatterns = [
    path('', lambda request: HttpResponse(
        '<h1>API Clínica</h1>'
        '<p><a href="/admin/">Admin</a> | '
        '<a href="/api/doctores/">Doctores</a> | '
        '<a href="/api/citas/">Citas</a> | '
        '<a href="/api/cuentas/">Cuentas</a> | '
        '<a href="/api/diagnosticos/">Diagnosticos</a></p>'
    )),
    path('admin/', admin.site.urls),
    path('api/cuentas/', include('apps.cuentas.urls')),
    path('api/doctores/', include('apps.doctores.urls')),
    path('api/citas/', include('apps.citas_pagos.urls')),
    path('api/diagnosticos/', include('apps.historiasDiagnosticos.urls')),  
]