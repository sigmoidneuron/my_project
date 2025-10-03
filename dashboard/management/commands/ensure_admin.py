from __future__ import annotations

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Ensures the default admin user exists without overriding existing credentials.'

    def handle(self, *args, **options):
        User = get_user_model()
        username = 'admin'
        password = '12345'
        if User.objects.filter(username=username).exists():
            self.stdout.write(self.style.SUCCESS('Admin user already exists. No changes made.'))
            return
        user = User.objects.create_superuser(username=username, password=password, email='')
        self.stdout.write(self.style.SUCCESS('Created default admin user (admin/12345).'))
