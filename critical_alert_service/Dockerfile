# Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Устанавливаем зависимости
RUN pip install --no-cache-dir pika requests

# Копируем сервис
COPY critical_alert_service.py .

# Создаем тестовый скрипт (будет ниже)
COPY test_api_gateway.py .

# Запускаем сервис
CMD ["python", "-u", "critical_alert_service.py"]