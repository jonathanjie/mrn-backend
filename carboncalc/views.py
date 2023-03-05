from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView

from carboncalc.serializers.cii_serializers import (
    CIICalculatorInputSerializer,
    CIICalculatorOutputSerializer,
    CIIConfigViewSerlaizer,
    EnergyEfficiencyTechnicalFileSerializer,
    ShipOverviewCIISerializer,
    StandardizedDataReportingFileSerializer,
)
from carboncalc.logic.cii_logic import process_cii_calculator
from carboncalc.tasks import (
    populate_cii_boundaries_for_ship_task,
    process_standardized_data_reporting_file_task,
)
from core.models import Ship


class CIIConfigView(generics.CreateAPIView):
    serializer_class = CIIConfigViewSerlaizer

    def create(self, request):
        ship = get_object_or_404(Ship, imo_reg=request.data.get('ship'))
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(ship=ship)
        headers = self.get_success_headers(serializer.data)
        populate_cii_boundaries_for_ship_task.delay(ship_imo=ship.imo_reg)
        return Response(serializer.data, status=status.HTTP_201_CREATED,
                        headers=headers)


class StandardizedDataReportingFile(generics.CreateAPIView):
    serializer_class = StandardizedDataReportingFileSerializer

    def create(self, request):
        ship = get_object_or_404(Ship, imo_reg=request.data.get('ship'))
        serializer = self.get_serializer(
            data=request.data, many=isinstance(request.data, list))
        # TODO: Handle multiple files
        serializer.is_valid(raise_exception=True)
        file = serializer.save(ship=ship)
        process_standardized_data_reporting_file_task.delay(
            file_uuid=file.uuid)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED,
                        headers=headers)


class EnergyEfficiencyTechnicalFileView(generics.CreateAPIView):
    serializer_class = EnergyEfficiencyTechnicalFileSerializer

    def create(self, request):
        ship = get_object_or_404(Ship, imo_reg=request.data.get('imo_reg'))
        serializer = self.get_serializer(
            data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(ship=ship)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED,
                        headers=headers)


class ShipsCIIOverviewListView(generics.ListAPIView):
    serializer_class = ShipOverviewCIISerializer

    def get_queryset(self):
        user = self.request.user
        ships = Ship.objects.filter(
            assigned_users=user,
        ).select_related(
            'shipspecs',
        )
        return ships


class CIICalculatorView(APIView):
    def post(self, request):
        ship = get_object_or_404(Ship, imo_reg=request.data.pop('ship'))
        input_serializer = CIICalculatorInputSerializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)
        calculations = process_cii_calculator(
            ship=ship,
            distance=input_serializer.validated_data.get('distance_in_period'),
            fuel_burn_dict=input_serializer.validated_data.get('fuel_consumption'),
            target_cii_grade=input_serializer.validated_data.get('target_cii_grade')
        )
        output_serializer = CIICalculatorOutputSerializer(calculations)
        return Response(output_serializer.data)
