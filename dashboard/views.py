from __future__ import annotations

import csv
import io
from decimal import Decimal, InvalidOperation

from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView
from django.db import IntegrityError
from django.core.paginator import Paginator
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.utils.http import urlencode
from django.views.decorators.http import require_POST

from catalog.models import PhoneNumber

from .forms import CSVUploadForm, PasswordUpdateForm, PhoneNumberForm

EXPECTED_HEADER = ['area code', 'phone number', 'cost']


class DashboardLoginView(LoginView):
    template_name = 'dashboard/login.html'
    redirect_authenticated_user = True


class DashboardLogoutView(LogoutView):
    next_page = reverse_lazy('dashboard:login')


@login_required
def home(request: HttpRequest) -> HttpResponse:
    sort = request.GET.get('sort', 'area_code')
    order = request.GET.get('order', 'asc')
    page_number = request.GET.get('page', 1)
    valid_sorts = {'area_code', 'local_number', 'cost'}
    if sort not in valid_sorts:
        sort = 'area_code'
    if order not in {'asc', 'desc'}:
        order = 'asc'
    ordering = sort if order == 'asc' else f'-{sort}'
    queryset = PhoneNumber.objects.order_by(ordering)

    paginator = Paginator(queryset, 25)
    page_obj = paginator.get_page(page_number)
    serial_start = (page_obj.number - 1) * paginator.per_page

    params = request.GET.copy()
    if 'page' in params:
        del params['page']
    base_query = urlencode(params, doseq=True)

    context = {
        'page_obj': page_obj,
        'sort': sort,
        'order': order,
        'serial_start': serial_start,
        'base_query': base_query,
    }
    return render(request, 'dashboard/index.html', context)


@login_required
def phone_create(request: HttpRequest) -> HttpResponse:
    if request.method == 'POST':
        form = PhoneNumberForm(request.POST)
        if form.is_valid():
            try:
                form.save()
            except IntegrityError:
                form.add_error(None, 'This phone number already exists.')
            else:
                messages.success(request, 'Phone number added.')
                return redirect('dashboard:home')
    else:
        form = PhoneNumberForm()
    return render(request, 'dashboard/form.html', {'form': form, 'title': 'Add Phone Number'})


@login_required
def phone_update(request: HttpRequest, pk: int) -> HttpResponse:
    phone = get_object_or_404(PhoneNumber, pk=pk)
    if request.method == 'POST':
        form = PhoneNumberForm(request.POST, instance=phone)
        if form.is_valid():
            try:
                form.save()
            except IntegrityError:
                form.add_error(None, 'Another entry with this area code and phone number already exists.')
            else:
                messages.success(request, 'Phone number updated.')
                return redirect('dashboard:home')
    else:
        form = PhoneNumberForm(instance=phone)
    return render(request, 'dashboard/form.html', {'form': form, 'title': 'Edit Phone Number'})


@login_required
@require_POST
def phone_delete(request: HttpRequest, pk: int) -> HttpResponse:
    phone = get_object_or_404(PhoneNumber, pk=pk)
    phone.delete()
    messages.success(request, 'Phone number deleted.')
    return redirect('dashboard:home')


@login_required
def delete_all(request: HttpRequest) -> HttpResponse:
    if request.method == 'POST':
        deleted, _ = PhoneNumber.objects.all().delete()
        messages.success(request, f'Removed {deleted} phone numbers.')
        return redirect('dashboard:home')
    return render(request, 'dashboard/confirm_delete_all.html')


@login_required
def upload_csv(request: HttpRequest) -> HttpResponse:
    summary: dict[str, object] | None = None
    details: list[str] = []
    if request.method == 'POST':
        form = CSVUploadForm(request.POST, request.FILES)
        if form.is_valid():
            uploaded = form.cleaned_data['csv_file']
            uploaded.seek(0)
            text_file = io.TextIOWrapper(uploaded.file, encoding='utf-8', newline='')
            try:
                reader = csv.reader(text_file)
                try:
                    header = next(reader)
                except StopIteration:
                    form.add_error('csv_file', 'CSV file is empty.')
                else:
                    normalized = [col.strip() for col in header]
                    if normalized != EXPECTED_HEADER:
                        form.add_error('csv_file', 'CSV header must be exactly: area code,phone number,cost')
                    else:
                        inserted = updated = skipped = 0
                        for line_number, row in enumerate(reader, start=2):
                            if len(row) != 3:
                                skipped += 1
                                details.append(f'Line {line_number}: expected 3 columns, found {len(row)}.')
                                continue
                            area_code, local_number, cost_value = [item.strip() for item in row]
                            if not area_code.isdigit() or len(area_code) != 3:
                                skipped += 1
                                details.append(f'Line {line_number}: invalid area code.')
                                continue
                            if not local_number.isdigit() or len(local_number) != 7:
                                skipped += 1
                                details.append(f'Line {line_number}: invalid phone number.')
                                continue
                            try:
                                cost_decimal = Decimal(cost_value)
                            except (InvalidOperation, ValueError):
                                skipped += 1
                                details.append(f'Line {line_number}: invalid cost value.')
                                continue
                            _, created = PhoneNumber.objects.update_or_create(
                                area_code=area_code,
                                local_number=local_number,
                                defaults={'cost': cost_decimal},
                            )
                            if created:
                                inserted += 1
                            else:
                                updated += 1
                        summary = {
                            'inserted': inserted,
                            'updated': updated,
                            'skipped': skipped,
                        }
                        if skipped:
                            messages.warning(request, 'CSV processed with some skipped rows.')
                        else:
                            messages.success(request, 'CSV processed successfully.')
            finally:
                text_file.detach()
    else:
        form = CSVUploadForm()
    context = {'form': form, 'summary': summary, 'details': details}
    return render(request, 'dashboard/upload.html', context)


@login_required
def update_password(request: HttpRequest) -> HttpResponse:
    if request.method == 'POST':
        form = PasswordUpdateForm(request.user, request.POST)
        if form.is_valid():
            new_password = form.cleaned_data['new_password']
            user = request.user
            user.set_password(new_password)
            user.save()
            logout(request)
            messages.success(request, 'Password updated. Please sign in with your new password.')
            return redirect('dashboard:login')
    else:
        form = PasswordUpdateForm(request.user)
    return render(request, 'dashboard/password_update.html', {'form': form})
