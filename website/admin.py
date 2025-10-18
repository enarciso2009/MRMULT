from django.contrib import admin
from .models import Empresa, Profile

@admin.register(Empresa)
class EmpresaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'cnpj')

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'empresa')
    list_filter = ('empresa',)

