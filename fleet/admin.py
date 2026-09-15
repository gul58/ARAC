from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from .models import Company, Driver, Foreman, Region, User, Vehicle, VehicleTask


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    list_display = ("username", "email", "role", "is_staff", "is_active")
    list_filter = ("role", "is_staff", "is_active")
    fieldsets = DjangoUserAdmin.fieldsets + (("Rol", {"fields": ("role",)}),)
    add_fieldsets = DjangoUserAdmin.add_fieldsets + (("Rol", {"fields": ("role",)}),)


admin.site.register(Region)
admin.site.register(Company)
admin.site.register(Foreman)
admin.site.register(Vehicle)
admin.site.register(Driver)
admin.site.register(VehicleTask)
