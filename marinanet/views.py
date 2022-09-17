from functools import wraps

from django.http import JsonResponse
from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny


@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def test(request):
    return JsonResponse({'message': 'TESTED'})
