web: gunicorn email_automation.wsgi:application --log-file - --log-level debug
celery: celery -A email_automation worker -l error -B --scheduler django_celery_beat.schedulers:DatabaseScheduler
