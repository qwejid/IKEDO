from __future__ import absolute_import, unicode_literals
import os
from celery import Celery

# Установливаю переменную окружения DJANGO_SETTINGS_MODULE в 'IKEDO.settings'
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'IKEDO.settings')

# Создаю экземпляр Celery и указываю имя проекта
app = Celery('IKEDO')

# Загружаю настройки из файла settings.py
app.config_from_object('django.conf:settings', namespace='CELERY')

# Автоматически обнаруживаю и регистрирую задачи в приложениях Django
app.autodiscover_tasks()