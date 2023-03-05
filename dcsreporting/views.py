from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.response import Response

from core.models import Ship
from dcsreporting.serializers.file_serializers import DCSUploadedFileSerializer


class DCSUploadedFileView(generics.CreateAPIView):
    serializer_class = DCSUploadedFileSerializer

    def create(self, request):
        ship = get_object_or_404(Ship, imo_reg=request.data.get('ship'))
        serializer = self.get_serializer(
            data=request.data, many=isinstance(request.data, list))
        # TODO: Handle multiple files
        serializer.is_valid(raise_exception=True)
        serializer.save(ship=ship)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED,
                        headers=headers)
