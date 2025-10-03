from __future__ import annotations

from typing import Iterable

from django.db.models import IntegerField, Value
from django.db.models.functions import Abs, Cast
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import PhoneNumber
from .serializers import PhoneNumberSerializer


class AreaCodesView(APIView):
    """Return all distinct area codes."""

    authentication_classes: list = []
    permission_classes: list = []

    def get(self, request: Request) -> Response:
        area_codes: Iterable[str] = (
            PhoneNumber.objects.values_list('area_code', flat=True)
            .distinct()
            .order_by('area_code')
        )
        return Response({'area_codes': list(area_codes)})


class SearchView(APIView):
    """Search phone numbers by area code and seven-digit input."""

    authentication_classes: list = []
    permission_classes: list = []

    def get(self, request: Request) -> Response:
        area_code = request.query_params.get('area_code', '')
        digits = request.query_params.get('digits', '')
        top_param = request.query_params.get('top')

        errors = {}
        if not area_code.isdigit() or len(area_code) != 3:
            errors['area_code'] = 'area_code must be exactly 3 digits.'
        if not digits.isdigit() or len(digits) != 7:
            errors['digits'] = 'digits must be exactly 7 digits.'

        top = 50
        if top_param:
            if not top_param.isdigit():
                errors['top'] = 'top must be an integer between 1 and 100.'
            else:
                top = int(top_param)
                if not 1 <= top <= 100:
                    errors['top'] = 'top must be between 1 and 100.'
        if errors:
            return Response(errors, status=status.HTTP_400_BAD_REQUEST)

        target_number = int(digits)
        queryset = (
            PhoneNumber.objects.filter(area_code=area_code)
            .annotate(
                distance=Abs(
                    Cast('local_number', output_field=IntegerField())
                    - Value(target_number, output_field=IntegerField())
                )
            )
            .order_by('distance', 'local_number')
        )[:top]

        serializer = PhoneNumberSerializer(queryset, many=True)
        return Response(serializer.data)
