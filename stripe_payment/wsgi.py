"""
WSGI config for stripe_payment project.
"""
import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stripe_payment.settings')

application = get_wsgi_application()
