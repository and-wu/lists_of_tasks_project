# Используем официальный Python-образ как базовый
FROM python:3.13

# Устанавливаем рабочую директорию внутри контейнера
WORKDIR /app

# Копируем файл зависимостей в контейнер
COPY requirements.txt .

# добавляем в Dockerfile установку необходимых библиотек (например libGL.so.1)
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем весь проект в контейнер
COPY . .

# Указываем команду по умолчанию для запуска приложения
# Например, если ваше приложение запускается через app.py
CMD ["python", "main.py"]
