from django.http import Http404
from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from marinanet.models import (
    BunkerData,
    FreshWaterData,
    HeavyWeatherData,
    NoonReportAtSea,
    ReportHeader,
    Ship,
    Voyage,
    WeatherData,
)
from marinanet.permissions import (
    IsShipUser
)
from marinanet.serializers import (
    BunkerDataSerializer,
    FreshWaterDataSerializer,
    HeavyWeatherDataSerializer,
    NoonReportAtSeaSerializer,
    ReportHeaderSerializer,
    ShipSerializer,
    VoyageSerializer,
    WeatherDataSerializer,
)


""" SHIP VIEWS
"""


class ShipList(generics.ListAPIView):
    """
    List all Ships that a user can view
    """
    permission_classes = [IsShipUser]
    serializer_class = ShipSerializer

    def get_queryset(self):
        user = self.request.user
        queryset = Ship.objects.filter(assigned_users=user)
        return queryset


class ShipDetail(generics.RetrieveUpdateAPIView):
    """
    Displays details for a single ship
    User must have permission to view the ship
    """
    permission_classes = [IsShipUser]
    serializer_class = ShipSerializer
    lookup_field = 'imo_reg'

    def get_queryset(self):
        imo_reg = self.kwargs['imo_reg']
        queryset = Ship.objects.filter(imo_reg=imo_reg)
        return queryset


class ShipVoyageList(generics.ListAPIView):
    """
    List all Voyages from a single ship
    """
    serializer_class = VoyageSerializer

    def get_queryset(self):
        imo_reg = self.kwargs['imo_reg']
        ship = Ship.objects.get(imo_reg=imo_reg)
        queryset = Voyage.objects.filter(ship=ship)
        return queryset


class VoyageList(generics.ListCreateAPIView):
    """
    List all voyages that a user can view
    Creates voyage based on Ship UUID
    """
    serializer_class = VoyageSerializer

    def get_queryset(self):
        user = self.request.user
        queryset = Voyage.objects.filter(ship__assigned_users=user)
        return queryset

    def create(self, request):
        ship = get_object_or_404(Ship, uuid=request.data.get('ship_uuid'))
        # TODO: CHECK PERMISSIONS
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(ship=ship)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED,
                        headers=headers)


class VoyageDetail(generics.RetrieveAPIView):
    """
    Displays details for a single voyage based on UUID
    User must have permission to view ship that voyage is associated with
    """
    serializer_class = VoyageSerializer
    lookup_field = 'uuid'

    def get_queryset(self):
        user = self.request.user
        queryset = Voyage.objects.filter(ship__assigned_users=user)
        return queryset


class VoyageReportsList(generics.ListAPIView):
    serializer_class = ReportHeaderSerializer

    def get_queryset(self):
        voyage_uuid = self.kwargs['uuid']
        voyage = Voyage.objects.get(uuid=voyage_uuid)
        queryset = ReportHeader.objects.filter(voyage=voyage)
        return queryset


class NoonReport(APIView):
    permission_classes = [IsShipUser]

    def get_report_header(self, pk):
        try:
            report_header = ReportHeader.objects.select_related().get(pk=pk)
            return report_header
        except ReportHeader.DoesNotExist:
            raise Http404

    def get(self, request, pk):
        header = self.get_report_header(pk)
        voyage = header.voyage
        ship = voyage.ship
        self.check_object_permissions(request, ship)

        header_serializer = ReportHeaderSerializer(header)
        voyage_serializer = VoyageSerializer(voyage)
        ship_serializer = ShipSerializer(ship)

        noon_report = header.noonreportatsea
        noon_report_serializer = NoonReportAtSeaSerializer(noon_report)
        # weather = header.weatherdata
        # TODO: heavy weather data
        # bunker = header.bunkerdata
        # freshwater = header.freshwaterdata

        response = {
            'report_header': header_serializer.data,
            'voyage': voyage_serializer.data,
            'ship': ship_serializer.data,
        }
        return Response(response)

    def post(self, request):
        pass
