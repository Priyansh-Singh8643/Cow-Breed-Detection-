import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User

username = 'admin'
email = 'admin@example.com'
password = 'admin'

if not User.objects.filter(username=username).exists():
    print(f"Creating superuser: {username}")
    User.objects.create_superuser(username, email, password)
    print("Superuser created.")
else:
    print("Superuser already exists.")
