import sys
import os
import django
from django.conf import settings

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
try:
    django.setup()
except Exception as e:
    print(f"Django setup failed: {e}")

print(f"CWD: {os.getcwd()}")
print(f"Sys Path: {sys.path}")

try:
    import webapp
    print(f"Imported webapp: {webapp}")
except ImportError as e:
    print(f"Failed to import webapp: {e}")

try:
    import webapp.urls
    print(f"Imported webapp.urls: {webapp.urls}")
except ImportError as e:
    print(f"Failed to import webapp.urls: {e}")
except Exception as e:
    print(f"Error importing webapp.urls: {e}")
