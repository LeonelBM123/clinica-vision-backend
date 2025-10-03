def get_actor_usuario_from_request(request):
    """
    Intenta obtener el usuario actor desde el request.
    Retorna None si no se puede obtener.
    """
    try:
        # Si tienes autenticación por token
        if hasattr(request, 'user') and request.user.is_authenticated:
            # Buscar el Usuario correspondiente por email
            from .models import Usuario
            return Usuario.objects.filter(correo=request.user.email).first()
        return None
    except:
        return None

def log_action(request, accion, objeto=None, usuario=None):
    """
    Registra una acción en la bitácora.
    """
    try:
        from .models import Bitacora
        
        # Obtener IP del request
        ip = get_client_ip(request)
        
        # Crear registro de bitácora
        Bitacora.objects.create(
            usuario=usuario,
            accion=accion,
            ip=ip,
            objeto=objeto
        )
    except Exception as e:
        # En caso de error, no fallar la operación principal
        print(f"Error al registrar en bitácora: {e}")

def get_client_ip(request):
    """
    Obtiene la IP del cliente desde el request.
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip