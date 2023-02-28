from django.shortcuts import get_object_or_404, render
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView

from carboncalc.serializers.cii_serializers import (
    CIIConfigViewSerlaizer,
    EnergyEfficiencyTechnicalFileSerializer,
    StandardizedDataReportingFileSerializer,
)
from carboncalc.tasks import process_uploaded_data_report
from core.models import Ship


class CIIConfigView(generics.CreateAPIView):
    serializer_class = CIIConfigViewSerlaizer

    def create(self, request):
        ship = get_object_or_404(Ship, imo_reg=request.data.get('imo_reg'))
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(ship=ship)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED,
                        headers=headers)


class StandardizedDataReportingFile(generics.CreateAPIView):
    serializer_class = StandardizedDataReportingFileSerializer

    def create(self, request):
        ship = get_object_or_404(Ship, imo_reg=request.data.get('ship'))
        serializer = self.get_serializer(
            data=request.data, many=isinstance(request.data, list))
        serializer.is_valid(raise_exception=True)
        file = serializer.save(ship=ship)
        process_uploaded_data_report.delay(file.uuid)
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
