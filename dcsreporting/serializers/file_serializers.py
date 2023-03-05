from rest_framework import serializers

from core.serializers import ShipSerializer
from dcsreporting.models import DCSUploadedFile

class DCSUploadedFileSerializer(serializers.ModelSerializer):
    ship = ShipSerializer(read_only=True)

    class Meta:
        model = DCSUploadedFile
        fields = ['uuid', 'file_name', 's3_file_path',
                  'ship', 'year']
