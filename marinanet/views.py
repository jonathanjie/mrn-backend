from datetime import datetime, timedelta, timezone

from django.db.models import Q
from django.db.models.functions import TruncDate
from django.forms.models import model_to_dict
from django.http import Http404
from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.serializers import ModelSerializer
from rest_framework.views import APIView
from rest_framework import status

# from marinanet.enums import ReportTypes
from marinanet.enums import ReportType
from marinanet.models import (
    ReportHeader,
    ReportRoute,
    Ship,
    ShipSpecs,
    UserProfile,
    Voyage,
    VoyageLeg,
    VoyageLegData,
)
from marinanet.permissions import (
    IsShipUser
)
from marinanet.serializers.model_serializers import (
    ReportHeaderSerializer,
    ReportHeaderWithLegSerializer,
    ShipSerializer,
    ShipSpecsSerializer,
    UserProfileSerializer,
    VoyageLegSerializer,
    VoyageLegDataSerializer,
    VoyageLegWithPortsSerializer,
    VoyageReportsSerializer,
    VoyageSerializer,
)
from marinanet.serializers.stats_serializers import (
    DailyStatSerializer,
    VesselListDetailSerializer,
)
from marinanet.utils.serializer_utils import get_serializer_from_report_type

import logging

logger = logging.getLogger(__name__)

""" USER VIEWS
"""


class UserProfileView(APIView):
    def get(self, request):
        user = request.user
        user_profile = get_object_or_404(UserProfile, user=user)
        serializer = UserProfileSerializer(user_profile)
        return Response(serializer.data)


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
        queryset = Ship.objects.filter(assigned_users=user).select_related(
            'shipspecs')  # TODO: Why can't this be "ship_specs"?
        print(queryset)
        return queryset


class ShipDetail(generics.RetrieveAPIView):
    queryset = Ship.objects.all()
    serializer_class = ShipSerializer
    lookup_field = 'imo_reg'



# class ShipDetail(APIView):
#     def get(self, request, imo_reg):
#         print("REQUEST:")
#         print((request.body).decode('utf-8'))
#         ship = get_object_or_404(Ship, imo_reg=imo_reg)
#         ship_serializer = ShipSerializer(ship)
#         if hasattr(ship, 'specs'):
#             ship_specs = ship.specs
#             ship_specs_serializer = ShipSpecsSerializer(ship_specs)
#             data = ship_serializer.data
#             data['specs'] = ship_specs_serializer.data
#             return Response(data)
#         else:
#             data = ship_serializer.data
#             return Response(data)


class ShipOverviewList(generics.ListAPIView):
    serializer_class = VesselListDetailSerializer

    def get_queryset(self):
        user = self.request.user
        queryset = VoyageLeg.objects.filter(
            voyage__ship__assigned_users=user
            ).order_by(
                'voyage__ship',
                '-modified_at'
            ).distinct(
                'voyage__ship'
            ).select_related(
                'voyage__ship__shipspecs',
                'voyagelegdata',
            )
        return queryset


class ShipSpecsCreate(APIView):
    def post(self, request, imo_reg):
        print("REQUEST:")
        print((request.body).decode('utf-8'))
        ship = get_object_or_404(Ship, imo_reg=imo_reg)
        ship.ship_type = request.data['ship_type']
        ship.save()

        try:
            ship_specs = ship.shipspecs
        except ShipSpecs.DoesNotExist:
            # ShipSpecs object does not exist, so create it
            serializer = ShipSpecsSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save(ship=ship)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            # ShipSpecs object exists, so update it
            serializer = ShipSpecsSerializer(ship_specs, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


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
        ship = get_object_or_404(Ship, imo_reg=request.data.get('imo_reg'))
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
        voyage_uuid = self.kwargs['uuid']
        queryset = Voyage.objects.filter(uuid=voyage_uuid)
        return queryset


class LatestVoyageDetailByShip(generics.RetrieveAPIView):
    """
    Displays details for the latest report for a ship
    User must have permission to view ship that voyage is associated with
    """
    serializer_class = VoyageSerializer
    lookup_field = 'imo_reg'

    def get_queryset(self):
        imo_reg = self.kwargs['imo_reg']
        user = self.request.user
        ship = Ship.objects.get(imo_reg=imo_reg)
        queryset = Voyage.objects.filter(ship=ship)
        return queryset

    def get_object(self):
        queryset = self.get_queryset()
        return queryset.latest('created_at')


class VoyageReportsList(generics.ListAPIView):
    """
    Lists all reports from a single voyage
    TODO: User must have permission to view ship
    """
    serializer_class = ReportHeaderWithLegSerializer

    def get_queryset(self):
        voyage_uuid = self.kwargs['uuid']
        voyage = Voyage.objects.get(uuid=voyage_uuid)
        queryset = ReportHeader.objects.filter(voyage_leg__voyage=voyage)
        return queryset


class ShipReportsList(generics.ListAPIView):
    """
    Lists all reports from a single ship
    """
    serializer_class = VoyageReportsSerializer

    def get_queryset(self):
        imo_reg = self.kwargs['imo_reg']
        ship = Ship.objects.get(imo_reg=imo_reg)
        queryset = Voyage.objects.filter(ship=ship)
        return queryset


class ReportsList(generics.ListCreateAPIView):
    """
    Lists all reports that a user can view
    Creates a new report
    """
    serializer_class = ReportHeaderSerializer

    def get_queryset(self):
        user = self.request.user
        queryset = ReportHeader.objects.filter(
            voyage_leg__voyage__ship__assigned_users=user)
        return queryset

    def create(self, request, *args, **kwargs):
        # Get the report type from the request data
        report_type = request.data.get('report_type')

        # Temporary logic for creating new VoyageLeg
        # TODO: Creation of VoyageLeg should be separate API
        if report_type == ReportType.DEP_SBY:
            voyage_leg_data = request.data.pop('voyage_leg')
            voyage_uuid = voyage_leg_data.pop('voyage').pop('uuid')
            voyage = Voyage.objects.get(uuid=voyage_uuid)
            voyage_leg, _ = VoyageLeg.objects.get_or_create(
                voyage=voyage, **voyage_leg_data)
        else:
            voyage_leg_data = request.data.pop('voyage_leg')
            voyage_leg = VoyageLeg.objects.get(uuid=voyage_leg_data['uuid'])

        # Get serializer class based on report type
        serializer_class = get_serializer_from_report_type(report_type)
        serializer = serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Save the newly created report header
        serializer.save(voyage_leg=voyage_leg)
        headers = self.get_success_headers(serializer.data)

        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class ReportDetail(generics.RetrieveAPIView):
    """
    Displays details for a single Noon Report At Sea based on UUID
    TODO: User must have permission to view ship
    """
    lookup_field = 'uuid'

    def get_queryset(self):
        report_uuid = self.kwargs['uuid']
        queryset = ReportHeader.objects.filter(uuid=report_uuid)
        return queryset

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        report_type = instance.report_type
        serializer_class = get_serializer_from_report_type(report_type)
        serializer = serializer_class(instance)
        return Response(serializer.data)


class LatestReportDetailByShip(generics.RetrieveAPIView):
    """
    Displays details for the latest report for a given ship.
    """
    lookup_field = 'imo_reg'

    def get_queryset(self):
        imo_reg = self.kwargs['imo_reg']
        queryset = ReportHeader.objects.filter(
            voyage_leg__voyage__ship__imo_reg=imo_reg
        ).order_by('-report_date')
        return queryset.first()

    def get_object(self):
        queryset = self.get_queryset()
        obj = None
        if queryset:
            obj = queryset
        return obj

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        report_type = instance.report_type
        serializer_class = get_serializer_from_report_type(report_type)
        serializer = serializer_class(instance)
        return Response(serializer.data)


class ShipLegsList(generics.ListAPIView):
    """
    Lists all legs from a single ship
    """
    serializer_class = VoyageLegWithPortsSerializer

    def get_queryset(self):
        imo_reg = self.kwargs['imo_reg']
        ship = Ship.objects.get(imo_reg=imo_reg)
        queryset = VoyageLeg.objects.filter(
            voyage__ship=ship
        ).select_related(
            'voyagelegdata',
        ).order_by(
            'created_at',
        )
        return queryset


class ReportPrefillView(generics.RetrieveAPIView):
    serializer_class = VoyageLegDataSerializer
    lookup_field = 'imo_reg'

    def get_queryset(self):
        imo_reg = self.kwargs['imo_reg']
        ship = Ship.objects.get(imo_reg=imo_reg)
        queryset = VoyageLegData.objects.filter(voyage_leg__voyage__ship=ship)
        return queryset

    def get_object(self):
        queryset = self.get_queryset()
        obj = {}
        if queryset:
            obj = queryset.latest('modified_at')
        return obj


class WeeklyStatsList(APIView):
    def get(self, request, imo_reg):
        ship = get_object_or_404(Ship, imo_reg=imo_reg)
        past_week_reports = ReportHeader.objects.filter(
            Q(report_type=ReportType.DEP_SBY) |
            Q(report_type=ReportType.DEP_COSP) |
            Q(report_type=ReportType.NOON) |
            Q(report_type=ReportType.ARR_SBY) |
            Q(report_type=ReportType.ARR_FWE)
        ).order_by(
            '-report_date',
        ).select_related(
            'distancetimedata',
        ).prefetch_related(
            'consumptionconditiondata__fueloildata_set',
        )[:7]

        serializer = DailyStatSerializer(past_week_reports, many=True)
        return Response(serializer.data)
