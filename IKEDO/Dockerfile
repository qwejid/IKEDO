# Использую официальный образ Python
FROM python:3.9.13

# Установливаю рабочую директорию в /IKEDO
WORKDIR /IKEDO

# Копирую файлы для установки зависимостей
COPY requirements.txt .
COPY requirements-dev.txt .  

# Установливаю зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копирую содержимое текущего каталога в контейнер в /app
COPY . .

# Открываю порт 8000
EXPOSE 8000

# Запускаю команду при запуске контейнера
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
