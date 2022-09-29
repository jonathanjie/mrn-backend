from django.http import Http404
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from marinanet.models import (
    Ship
)
from marinanet.permissions import (
    IsShipUser
)
from marinanet.serializers import (
    ShipSerializer
)

# Ship
@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def ship_list(request):
    """
    List all ships, or create new ship
    """
    if request.method == "GET":
        ships = Ship.objects.all()
        serializer = ShipSerializer(ships, many=True)
        return Response(serializer.data)

    elif request.method == "POST":
        serializer = ShipSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ShipDetail(APIView):
    permission_classes = [IsShipUser]

    def get_object(self, pk):
        try:
            return Ship.objects.get(id=pk)
        except Ship.DoesNotExist:
            raise Http404

    def get(self, request, pk):
        ship = self.get_object(pk)
        self.check_object_permissions(request, ship)
        serializer = ShipSerializer(ship)
        return Response(serializer.data)


class NoonReport(APIView):
    permission_classes = []

    def get(self, request, pk):
        pass

    def post(self, request):
        pass
