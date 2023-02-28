from django.contrib import admin

# Register your models here.
from carboncalc.models import (
    CalculatedCII,
    CIIConfig,
    CIIRawData,
    CIIShipYearBoundaries,
    EnergyEfficiencyTechnicalFile,
    StandardizedDataReportingData,
    StandardizedDataReportingFile,
    TargetCII,
)


admin.site.register(CIIConfig)
admin.site.register(TargetCII)
admin.site.register(CalculatedCII)
admin.site.register(CIIRawData)
admin.site.register(CIIShipYearBoundaries)
admin.site.register(StandardizedDataReportingFile)
admin.site.register(StandardizedDataReportingData)
admin.site.register(EnergyEfficiencyTechnicalFile)
