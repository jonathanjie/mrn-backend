from django.shortcuts import render
from rest_framework import generics
from rest_framework.views import APIView

from carboncalc.serializers.cii_serializers import (
    CIIConfigViewSerlaizer,
    EnergyEfficiencyTechnicalFileSerializer,
    StandardizedDataReportingFile,
)


class CIIConfigView(generics.CreateAPIView):
    serializer_class = VoyageSerializer

    def create(self, request):
        ship = get_object_or_404(Ship, imo_reg=request.data.get('imo_reg'))
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(ship=ship)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED,
                        headers=headers)


class StandardizedDataReportingFile(generics.CreateAPIView):
    serializer_class = StandardizedDataReportingFile

    def create(self, request):
        ship = get_object_or_404(Ship, imo_reg=request.data.get('imo_reg'))
        serializer = self.get_serializer(
            data=request.data, many=isinstance(request.data, list))
        serializer.is_valid(raise_exception=True)
        serializer.save(ship=ship)
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
