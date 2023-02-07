from django.contrib import admin

# Register your models here.
from vesselreporting.models.report_models import (
    ActualPerformanceData,
    ArrivalFWETimeAndPosition,
    ArrivalPilotStation,
    ArrivalStandbyTimeAndPosition,
    BDNData,
    CargoOperation,
    ConsumptionConditionData,
    DeparturePilotStation,
    DepartureRunUp,
    DepartureVesselCondition,
    DistanceTimeData,
    EventData,
    FreshWaterData,
    FreshWaterTotalConsumptionData,
    FuelOilData,
    FuelOilDataCorrection,
    FuelOilTotalConsumptionData,
    FuelOilTotalConsumptionDataCorrection,
    HeavyWeatherData,
    LubricatingOilData,
    LubricatingOilDataCorrection,
    LubricatingOilTotalConsumptionData,
    LubricatingOilTotalConsumptionDataCorrection,
    NoonReportTimeAndPosition,
    PerformanceData,
    PortOperations,
    PlannedOperations,
    ReportHeader,
    ReportRoute,
    SailingPlan,
    StoppageData,
    TotalConsumptionData,
    Voyage,
    VoyageLeg,
    VoyageLegData,
    WeatherData
)
from vesselreporting.models.ship_models import (
    Ship,
    ShipSpecs,
    ShipUser,
)


class ShipAdmin(admin.ModelAdmin):
    list_display = ('company', 'name', 'imo_reg')


# User and Company models
admin.site.register(Ship, ShipAdmin)
admin.site.register(ShipSpecs)
admin.site.register(ShipUser)

# Report Models
admin.site.register(Voyage)
admin.site.register(VoyageLeg)
admin.site.register(ReportHeader)
admin.site.register(NoonReportTimeAndPosition)
admin.site.register(ReportRoute)
admin.site.register(WeatherData)
admin.site.register(HeavyWeatherData)
admin.site.register(DistanceTimeData)
admin.site.register(PerformanceData)
admin.site.register(ConsumptionConditionData)
admin.site.register(FuelOilData)
admin.site.register(FuelOilDataCorrection)
admin.site.register(LubricatingOilData)
admin.site.register(LubricatingOilDataCorrection)
admin.site.register(FreshWaterData)
admin.site.register(StoppageData)
admin.site.register(CargoOperation)
admin.site.register(DepartureVesselCondition)
admin.site.register(DeparturePilotStation)
admin.site.register(ArrivalPilotStation)
admin.site.register(DepartureRunUp)
admin.site.register(SailingPlan)
admin.site.register(ArrivalStandbyTimeAndPosition)
admin.site.register(PlannedOperations)
admin.site.register(ActualPerformanceData)
admin.site.register(TotalConsumptionData)
admin.site.register(FuelOilTotalConsumptionData)
admin.site.register(FuelOilTotalConsumptionDataCorrection)
admin.site.register(LubricatingOilTotalConsumptionData)
admin.site.register(LubricatingOilTotalConsumptionDataCorrection)
admin.site.register(FreshWaterTotalConsumptionData)
admin.site.register(ArrivalFWETimeAndPosition)
admin.site.register(PortOperations)
admin.site.register(EventData)
admin.site.register(BDNData)
admin.site.register(VoyageLegData)
