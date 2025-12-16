from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
import os

User = get_user_model()

class Command(BaseCommand):
    help = 'Creates a default superuser for the database'

    def handle(self, *args, **options):
        # Default credentials
        USERNAME = 'admin'
        EMAIL = 'admin@example.com'
        PASSWORD = 'admin123'

        self.stdout.write("--- Creating Superuser ---")

        if not User.objects.filter(username=USERNAME).exists():
            self.stdout.write(f"User '{USERNAME}' not found. Creating...")
            User.objects.create_superuser(USERNAME, EMAIL, PASSWORD)
            self.stdout.write(self.style.SUCCESS(f"Superuser created successfully!\nUsername: {USERNAME}\nPassword: {PASSWORD}"))
        else:
            self.stdout.write(self.style.WARNING(f"Superuser '{USERNAME}' already exists. Skipping creation."))
