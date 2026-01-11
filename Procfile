web: python manage.py migrate && python manage.py load_sample_data && gunicorn stripe_payment.wsgi --bind 0.0.0.0:$PORT
