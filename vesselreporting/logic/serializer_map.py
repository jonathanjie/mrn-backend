from rest_framework.serializers import ModelSerializer

from vesselreporting.enums import ReportType
from vesselreporting.serializers.report_serializers import (
    ArrivalFWEReportViewSerializer,
    ArrivalStandbyReportViewSerializer,
    BDNReportViewSerializer,
    DepartureCOSPReportViewSerializer,
    DepartureStandbyReportViewSerializer,
    EventReportViewSerialiazer,
    NoonReportViewSerializer
)


def get_serializer_from_report_type(report_type: str) -> ModelSerializer:
    serializer_type_map = {
        ReportType.NOON: NoonReportViewSerializer,
        ReportType.DEP_SBY: DepartureStandbyReportViewSerializer,
        ReportType.DEP_COSP: DepartureCOSPReportViewSerializer,
        ReportType.ARR_SBY: ArrivalStandbyReportViewSerializer,
        ReportType.ARR_FWE: ArrivalFWEReportViewSerializer,
        ReportType.EVENT_HARBOUR: EventReportViewSerialiazer,
        ReportType.EVENT_PORT: EventReportViewSerialiazer,
        ReportType.NOON_HARBOUR: EventReportViewSerialiazer,
        ReportType.NOON_PORT: EventReportViewSerialiazer,
        ReportType.BDN: BDNReportViewSerializer,
    }
    return serializer_type_map.get(report_type)
