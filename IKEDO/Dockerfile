# Использую официальный образ Python
FROM python:3.9.13

# Установливаю рабочую директорию в /IKEDO
WORKDIR /IKEDO

# Копирую файлы для установки зависимостей
COPY requirements.txt .
 
# Установливаю зависимости
RUN apt-get update && apt-get install -y supervisor && apt-get clean && rm -rf /var/lib/apt/lists/*
RUN pip install --no-cache-dir -r requirements.txt

# Копирую содержимое текущего каталога в контейнер
COPY . .

COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf


# Откройте порты 8000 и 5555 (или другие, если используете другие порты для Django и Celery)
EXPOSE 8000

# Запустите Supervisor
CMD ["supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]