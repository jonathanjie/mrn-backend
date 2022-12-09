from django.contrib import admin

# Register your models here.
from marinanet.models import (
    Company,
    ConsumptionConditionData,
    ConsumptionDataCorrection,
    DistancePerformanceData,
    FreshWaterData,
    FuelOilData,
    FuelOilDataCorrection,
    HeavyWeatherData,
    LubricatingOilData,
    LubricatingOilDataCorrection,
    ReportHeader,
    Route,
    Ship,
    ShipSpecs,
    ShipUser,
    StoppageData,
    UserProfile,
    Voyage,
    WeatherData
)


class CompanyAdmin(admin.ModelAdmin):
    list_display = ('name',)


class ShipAdmin(admin.ModelAdmin):
    list_display = ('company', 'name', 'imo_reg')


# User and Company models
admin.site.register(Company, CompanyAdmin)
admin.site.register(UserProfile)
admin.site.register(Ship, ShipAdmin)
admin.site.register(ShipSpecs)
admin.site.register(ShipUser)

# Report Models
admin.site.register(Voyage)
admin.site.register(ReportHeader)
admin.site.register(Route)
admin.site.register(WeatherData)
admin.site.register(HeavyWeatherData)
admin.site.register(DistancePerformanceData)
admin.site.register(ConsumptionConditionData)
admin.site.register(FuelOilData)
admin.site.register(FuelOilDataCorrection)
admin.site.register(LubricatingOilData)
admin.site.register(LubricatingOilDataCorrection)
admin.site.register(FreshWaterData)
admin.site.register(StoppageData)
