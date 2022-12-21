from rest_framework.serializers import ModelSerializer

from marinanet.enums import ReportType
from marinanet.serializers import (
    DepartureStandbyReportViewSerializer,
    NoonReportViewSerializer,
)


def get_serializer_from_report_type(report_type: str) -> ModelSerializer:
    serializer_type_map = {
        ReportType.NOON: NoonReportViewSerializer,
        ReportType.DEP_SBY: DepartureStandbyReportViewSerializer,
    }
    return serializer_type_map.get(report_type)
