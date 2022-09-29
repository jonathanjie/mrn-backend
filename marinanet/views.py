from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from marinanet.models import (
    Ship
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


@api_view(['GET', 'PUT'])
@permission_classes([AllowAny])
def ship_detail(request, pk):
    try:
        ship = Ship.objects.get(pk=pk)
    except Ship.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == "GET":
        serializer = ShipSerializer(ship)
        return Response(serializer.data)

    elif request.method == "PUT":
        serializer = ShipSerializer(ship, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
