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

# User and Company models
admin.site.register(Company)
admin.site.register(Profile)
admin.site.register(Ship)
admin.site.register(ShipUser)

# Report Models
admin.site.register(Voyage)
admin.site.register(ReportHeader)
admin.site.register(NoonReportAtSea)
admin.site.register(WeatherData)
admin.site.register(HeavyWeatherData)
admin.site.register(BunkerData)
admin.site.register(FreshWaterData)
