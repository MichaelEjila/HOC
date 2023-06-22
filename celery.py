from celery import Celery

# Create a new Celery instance
app = Celery('HOC')

# Load the Celery configuration from Django settings
app.config_from_object('django.conf:settings', namespace='CELERY')

# Automatically discover and import task modules in your Django project
app.autodiscover_tasks()
