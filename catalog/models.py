from __future__ import annotations

from django.core.validators import RegexValidator
from django.db import models


digit_validator = RegexValidator(r'^\d+$', 'Digits only.')


class PhoneNumber(models.Model):
    area_code = models.CharField(max_length=3, validators=[digit_validator])
    local_number = models.CharField(max_length=7, validators=[digit_validator])
    cost = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['area_code', 'local_number'],
                name='unique_area_code_local_number',
            )
        ]
        indexes = [
            models.Index(fields=['area_code'], name='idx_area_code'),
            models.Index(fields=['local_number'], name='idx_local_number'),
        ]
        ordering = ['area_code', 'local_number']

    def __str__(self) -> str:  # pragma: no cover - simple representation
        return f"({self.area_code}) {self.local_number}"

    @property
    def full_number(self) -> str:
        return f"{self.area_code}{self.local_number}"
