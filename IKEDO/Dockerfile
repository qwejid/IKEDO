# Использую официальный образ Python
FROM python:3.9.13

# Установливаю рабочую директорию в app
WORKDIR /app

# Копирую файлы для установки зависимостей
COPY requirements.txt .
 
# Установливаю зависимости
RUN apt-get update && apt-get install -y supervisor && apt-get clean && rm -rf /var/lib/apt/lists/*
RUN pip install --no-cache-dir -r requirements.txt

# Копирую содержимое текущего каталога в контейнер
COPY . .



EXPOSE 8000


CMD ["supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]