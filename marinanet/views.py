from django.http import Http404
from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.serializers import ModelSerializer
from rest_framework.views import APIView

from marinanet.enums import ReportTypes
from marinanet.models import (
    ReportHeader,
    Ship,
    UserProfile,
    Voyage,
)
from marinanet.permissions import (
    IsShipUser
)
from marinanet.serializers import (
    NoonReportViewSerializer,
    ReportHeaderSerializer,
    ShipSerializer,
    UserProfileSerializer,
    VoyageReportsSerializer,
    VoyageSerializer
)
from marinanet.utils.serializer_utils import get_serializer_from_report_type

import logging

logger = logging.getLogger(__name__)

""" USER VIEWS
"""


class ProfileDetail(generics.RetrieveAPIView):
    """
    Displays profile of a user based on UUID
    User must have permission to view ship that voyage is associated with
    """
    logger.info("REQUESTING USER PROFILE")
    serializer_class = UserProfileSerializer
    # lookup_field = 'uuid'

    def get_queryset(self):
        user = self.request.user
        queryset = UserProfile.objects.filter(user=user)
        return queryset


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
    """
    Lists all reports from a single voyage
    TODO: User must have permission to view ship
    """
    serializer_class = ReportHeaderSerializer

    def get_queryset(self):
        voyage_uuid = self.kwargs['uuid']
        voyage = Voyage.objects.get(uuid=voyage_uuid)
        queryset = ReportHeader.objects.filter(voyage=voyage)
        return queryset


class ShipReportsList(generics.ListAPIView):
    """
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
            voyage__ship__assigned_users=user)
        return queryset

    def create(self, request, *args, **kwargs):
        report_type = request.data.get('report_type')
        # Get serializer class based on report type
        serializer_class = get_serializer_from_report_type(report_type)
        serializer = serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
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
