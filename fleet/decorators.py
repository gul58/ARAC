from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from functools import wraps


def role_required(*roles):
    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def _wrapped(request, *args, **kwargs):
            user = request.user
            if user.is_superuser:
                return view_func(request, *args, **kwargs)
            if user.role not in roles:
                raise PermissionDenied("Bu işlem için yetkiniz yok.")
            return view_func(request, *args, **kwargs)

        return _wrapped

    return decorator


def ihale_required(view_func):
    return role_required("ihale")(view_func)


def formen_required(view_func):
    return role_required("formen")(view_func)


def get_formen_or_403(user):
    if not user.is_authenticated:
        raise PermissionDenied
    profile = user.get_formen_profile()
    if user.is_formen and profile is None:
        raise PermissionDenied("Formen profiliniz tanımlı değil.")
    if user.is_formen:
        return profile
    raise PermissionDenied("Bu işlem yalnızca Formen kullanıcıları içindir.")


def formen_region_id(user):
    profile = get_formen_or_403(user)
    return profile.region_id
