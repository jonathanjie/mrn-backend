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

# import jwt
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


class ShipDetail(APIView):
    def get(self, request, imo_reg):
        print("REQUEST:")
        print((request.body).decode('utf-8'))
        ship = get_object_or_404(Ship, imo_reg=imo_reg)
        ship_serializer = ShipSerializer(ship)
        if hasattr(ship, 'specs'):
            ship_specs = ship.specs
            ship_specs_serializer = ShipSpecsSerializer(ship_specs)
            data = ship_serializer.data
            data['specs'] = ship_specs_serializer.data
            return Response(data)
        else:
            data = ship_serializer.data
            return Response(data)


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

    # def determine_new_allowed_report_types(allowed_report_types, report_type):

    #     all_report_types = ['NOON', 'DSBY',
    #                         'DCSP', 'ASBY', 'AFWE', 'BDN', 'EVENT']

    #     if report_type in ['NOON', 'BDN', 'EVENT']:
    #         return allowed_report_types
    #     elif report_type == 'DSBY':
    #         return all_report_types.remove('DSBY').remove('ASBY').remove('AFWE')
    #     elif report_type == 'DCSP':
    #         return all_report_types.remove('DSBY').remove('DCSP')
    #     elif report_type == 'ASBY':
    #         return all_report_types.remove('DSBY').remove('DCSP').remove('ASBY')
    #     elif report_type == 'AFWE':
    #         return all_report_types.remove('ASBY').remove('AFWE')
    #     else:
    #         return allowed_report_types
    #     # TODO: Check if these allows are correct

    def create(self, request, *args, **kwargs):
        # Get the report type from the request data
        report_type = request.data.get('report_type')

        # Temporary logic for creating new VoyageLeg
        # TODO: Creation of VoyageLeg should be separate API
        if report_type == ReportType.DEP_SBY:
            voyage_leg_data = request.data.pop('voyage_leg')
            voyage_uuid = voyage_leg_data.pop('voyage').pop('uuid')
            voyage = Voyage.objects.get(uuid=voyage_uuid)
            voyage_leg = VoyageLeg.objects.get_or_create(
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

        # # Fetch the voyage associated with the newly created report header
        # voyage = serializer.instance.voyage

        # # Determine the new allowed_report_types array based on the report_type
        # new_allowed_report_types = self.determine_new_allowed_report_types(report_type)

        # # Update the voyage's allowed_report_types array
        # voyage.allowed_report_types = new_allowed_report_types
        # voyage.save()

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


# class ShipLegsList(APIView):
#     def get(self, request, imo_reg):
#         # Get the ship with the given IMO number, or return a 404 response if it doesn't exist
#         ship = get_object_or_404(Ship, imo_reg=imo_reg)

#         # Get the latest voyage for the ship
#         latest_voyage = ship.voyage_set.order_by('-voyage_num').first()

#         # Return a 404 response if the ship has no voyages
#         if latest_voyage is None:
#             return Response(status=404)

#         # Get the number of voyage legs to return
#         count = request.query_params.get('count', 10)
#         count = int(count)

#         # Serialize the voyage legs for the latest voyages
#         voyage_legs = latest_voyage.voyageleg_set.order_by(
#             '-departure_date')[:count]
#         serializer = VoyageLegSerializer(voyage_legs, many=True)
#         return Response(serializer.data)


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


# class MostRecentDistinctReportRoutesList(generics.ListAPIView):
#     serializer_class = DistinctReportRoutesSerializer

#     def get_queryset(self):
#         imo_reg = self.kwargs['imo_reg']
#         ship = Ship.objects.get(imo_reg=imo_reg)

#         # Get the number of routes to query for from the request query parameters,
#         # or default to 10 if not provided
#         num_routes = self.request.query_params.get("num_routes", 10)

#         # Query for the most recent num_routes distinct ReportRoutes for the Ship,
#         # ordered by the report_date field in descending order
#         queryset = ReportRoute.objects.filter(
#             report_header__voyage__ship=ship
#         ).order_by("-report_header__report_date").values(
#             "departure_port", "arrival_port", "departure_date", "arrival_date"
#         ).distinct()

#         # If there are fewer than num_routes distinct routes for the Ship,
#         # only return the number of routes that are available
#         if queryset.count() < num_routes:
#             return queryset

#         # Otherwise, return the most recent num_routes routes
#         return queryset[:num_routes]


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
        ).select_related(
            'distancetimedata',
        ).prefetch_related(
            'consumptionconditiondata__fueloildata_set',
        )[:7]

        serializer = DailyStatSerializer(past_week_reports, many=True)
        return Response(serializer.data)
