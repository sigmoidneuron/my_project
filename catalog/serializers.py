from __future__ import annotations

from rest_framework import serializers

from .models import PhoneNumber


class PhoneNumberSerializer(serializers.ModelSerializer):
    full_number = serializers.CharField(read_only=True)

    class Meta:
        model = PhoneNumber
        fields = ['area_code', 'local_number', 'full_number', 'cost']
        read_only_fields = fields
