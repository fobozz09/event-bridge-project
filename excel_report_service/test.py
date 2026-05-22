import json
import pika
import uuid
from datetime import datetime

RABBITMQ_HOST = "localhost"
QUEUE_NAME = "excel_report_queue"

def send_test_requests():
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host=RABBITMQ_HOST)
    )
    channel = connection.channel()
    channel.queue_declare(queue=QUEUE_NAME, durable=True)
    
    # 5 тестовых запросов
    test_data = [
        {
            "id": str(uuid.uuid4()),
            "username": "ivan_petrov",
            "email": "ivan@example.com",
            "event_type": "register",
            "timestamp": datetime.now().isoformat(),
            "details": "Новая регистрация"
        },
        {
            "id": str(uuid.uuid4()),
            "username": "maria_s",
            "email": "maria@example.com",
            "event_type": "login",
            "timestamp": datetime.now().isoformat(),
            "details": "Вход в систему"
        },
        {
            "id": str(uuid.uuid4()),
            "username": "alex_k",
            "email": "alex@example.com",
            "event_type": "purchase",
            "timestamp": datetime.now().isoformat(),
            "details": "Покупка товара"
        },
        {
            "id": str(uuid.uuid4()),
            "username": "elena_v",
            "email": "elena@example.com",
            "event_type": "update_profile",
            "timestamp": datetime.now().isoformat(),
            "details": "Обновление профиля"
        },
        {
            "id": str(uuid.uuid4()),
            "username": "dmitry_z",
            "email": "dmitry@example.com",
            "event_type": "logout",
            "timestamp": datetime.now().isoformat(),
            "details": "Выход из системы"
        }
    ]
    
    for i, data in enumerate(test_data, 1):
        channel.basic_publish(
            exchange="",
            routing_key=QUEUE_NAME,
            body=json.dumps(data),
            properties=pika.BasicProperties(delivery_mode=2)
        )
        print(f"[✓] Запрос {i} отправлен: {data['username']} - {data['event_type']}")
    
    connection.close()
    print("\n✅ 5 запросов успешно отправлено!")

if __name__ == "__main__":
    send_test_requests()