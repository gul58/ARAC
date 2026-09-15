def user_role(request):
    user = getattr(request, "user", None)
    role = None
    formen_profile = None
    if user and user.is_authenticated:
        role = getattr(user, "role", None)
        formen_profile = getattr(user, "formen_profile", None)
    return {
        "current_role": role,
        "formen_profile": formen_profile,
    }
