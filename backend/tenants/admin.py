from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Tenant, User

admin.site.register(Tenant)
admin.site.register(User, UserAdmin)
