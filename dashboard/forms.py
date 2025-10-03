from __future__ import annotations

from typing import Any

from django import forms
from django.contrib.auth import password_validation
from django.core.exceptions import ValidationError

from catalog.models import PhoneNumber


class PhoneNumberForm(forms.ModelForm):
    class Meta:
        model = PhoneNumber
        fields = ['area_code', 'local_number', 'cost']
        widgets = {
            'area_code': forms.TextInput(attrs={'maxlength': 3, 'class': 'form-control'}),
            'local_number': forms.TextInput(attrs={'maxlength': 7, 'class': 'form-control'}),
            'cost': forms.NumberInput(attrs={'step': '0.01', 'class': 'form-control'}),
        }

    def clean_area_code(self) -> str:
        value = self.cleaned_data['area_code']
        if not value.isdigit() or len(value) != 3:
            raise ValidationError('Area code must be exactly 3 digits.')
        return value

    def clean_local_number(self) -> str:
        value = self.cleaned_data['local_number']
        if not value.isdigit() or len(value) != 7:
            raise ValidationError('Local number must be exactly 7 digits.')
        return value


class CSVUploadForm(forms.Form):
    csv_file = forms.FileField(label='CSV file (.csv only)', widget=forms.FileInput(attrs={'class': 'form-control'}))

    def clean_csv_file(self) -> Any:
        uploaded = self.cleaned_data['csv_file']
        content_type = uploaded.content_type or ''
        allowed_types = {'text/csv', 'application/csv', 'application/vnd.ms-excel', 'text/plain'}
        if content_type and content_type not in allowed_types:
            # Some browsers send application/vnd.ms-excel or text/plain for CSV
            raise ValidationError('Upload a valid CSV file.')
        if not uploaded.name.lower().endswith('.csv'):
            raise ValidationError('File extension must be .csv')
        return uploaded


class PasswordUpdateForm(forms.Form):
    current_password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    new_password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    confirm_new_password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    def clean_current_password(self) -> str:
        password = self.cleaned_data['current_password']
        if not self.user.check_password(password):
            raise ValidationError('Current password is incorrect.')
        return password

    def clean(self) -> dict[str, Any]:
        cleaned = super().clean()
        new_password = cleaned.get('new_password')
        confirm = cleaned.get('confirm_new_password')
        if new_password and confirm and new_password != confirm:
            self.add_error('confirm_new_password', 'New passwords do not match.')
        if new_password:
            password_validation.validate_password(new_password, self.user)
        return cleaned
