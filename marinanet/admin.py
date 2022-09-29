from django.contrib import admin

# Register your models here.
from marinanet.models import (
    BunkerData,
    Company,
    FreshWaterData,
    HeavyWeatherData,
    NoonReportAtSea,
    Profile,
    ReportHeader,
    Ship,
    ShipUser,
    Voyage,
    WeatherData
)


class CompanyAdmin(admin.ModelAdmin):
    list_display = ('name',)


class ShipAdmin(admin.ModelAdmin):
    list_display = ('company', 'name', 'imo_reg')


# User and Company models
admin.site.register(Company, CompanyAdmin)
admin.site.register(Profile)
admin.site.register(Ship, ShipAdmin)
admin.site.register(ShipUser)

# Report Models
admin.site.register(Voyage)
admin.site.register(ReportHeader)
admin.site.register(NoonReportAtSea)
admin.site.register(WeatherData)
admin.site.register(HeavyWeatherData)
admin.site.register(BunkerData)
admin.site.register(FreshWaterData)
