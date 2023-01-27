from django.contrib import admin

from core.models import (
    Company,
    User,
    UserProfile,
)


class CompanyAdmin(admin.ModelAdmin):
    list_display = ('name',)


# Register your models here.
admin.site.register(Company, CompanyAdmin)
admin.site.register(User)
admin.site.register(UserProfile)
