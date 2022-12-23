from rest_framework.serializers import ModelSerializer

from marinanet.enums import ReportType
from marinanet.serializers.report_serializers import (
    ArrivalFWEReportViewSerializer,
    ArrivalStandbyReportViewSerializer,
    DepartureCOSPReportViewSerializer,
    DepartureStandbyReportViewSerializer,
    NoonReportViewSerializer
)


def get_serializer_from_report_type(report_type: str) -> ModelSerializer:
    serializer_type_map = {
        ReportType.NOON: NoonReportViewSerializer,
        ReportType.DEP_SBY: DepartureStandbyReportViewSerializer,
        ReportType.DEP_COSP: DepartureCOSPReportViewSerializer,
        ReportType.ARR_SBY: ArrivalStandbyReportViewSerializer,
        ReportType.ARR_FWE: ArrivalFWEReportViewSerializer,
    }
    return serializer_type_map.get(report_type)
