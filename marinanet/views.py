from ./models import Author
from django.forms import modelformset_factory
from functools import wraps

from django.http import JsonResponse
from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response


"""
TESTING FUNCTIONS
"""


@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def test(request):
    print("METHOD: " + request.method)
    if request.method == 'POST':
        print("DATA:")
        print(request.data)
        return JsonResponse({"message": "Got some data!", "data": request.data})
    return JsonResponse({'message': 'TESTED'})


"""
REPORTS
"""

"""
- SUBMISSIONS
"""


@api_view(['POST'])
@permission_classes([AllowAny])
def submit_noon_report(request):
    """Sends noon report for validation then into DB"""
    report = request.data['report']

    print("REPORT:")
    print(report)

    validation = validate_noon_report(report)

    if (validation['has_error']):
        return JsonResponse({'message': 'VALIDATION ERROR'})

    return JsonResponse({'message': 'SUBMITTED'})


@api_view(['POST'])
@permission_classes([AllowAny])
def submit_departure_report(request):
    """Sends departure report for validation then into DB"""

    return JsonResponse({'message': 'SUBMITTED'})


@api_view(['POST'])
@permission_classes([AllowAny])
def submit_arrival_report(request):
    """Sends arrival report for validation then into DB"""

    return JsonResponse({'message': 'SUBMITTED'})


@api_view(['POST'])
@permission_classes([AllowAny])
def submit_bdn(request):
    """Sends bunker delivery for validation then into DB"""

    return JsonResponse({'message': 'SUBMITTED'})


"""
- VALIDATIONS
"""


def validate_noon_report(report=""):
    """Validates noon report"""

    return {
        "has_error": False,
        "errors": []
    }


"""
- DB INSERTION
"""

"""
FORMS
"""


def create_voyage(request):
    VoyageFormSet = modelformset_factory(
        Voyage, exclude=['uuid', 'ship', 'status', 'date_created', 'date_modified'])
    if request.method == 'POST':
        formset = VoyageFormSet(request.POST, request.FILES)
        if formset.is_valid():
            formset.save()
            # do something.
    else:
        formset = VoyageFormSet()
    return render(request, 'create_voyage.html', {'formset': formset})
