from django.contrib import admin

from core.models import (
    Company,
    Ship,
    ShipSpecs,
    ShipUser,
    User,
    UserProfile,
)


class CompanyAdmin(admin.ModelAdmin):
    list_display = ('name',)


# Register your models here.
admin.site.register(Company, CompanyAdmin)
admin.site.register(User)
admin.site.register(UserProfile)


class ShipAdmin(admin.ModelAdmin):
    list_display = ('company', 'name', 'imo_reg')


admin.site.register(Ship, ShipAdmin)
admin.site.register(ShipSpecs)
admin.site.register(ShipUser)
