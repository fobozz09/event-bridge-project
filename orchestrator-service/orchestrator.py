import pika
import sys
import os
from dotenv import load_dotenv
import time

# Загружаем переменные из .env
load_dotenv()

# Настройки подключения
HOST = os.getenv("RABBITMQ_HOST", "rabbitmq")
PORT = int(os.getenv("RABBITMQ_PORT", "5672"))
USER = os.getenv("RABBITMQ_USER", "guest")
PASSWORD = os.getenv("RABBITMQ_PASSWORD", "guest")

# Настройки RabbitMQ
EXCHANGE_NAME = 'event_topic_exchange'
EXCHANGE_TYPE = 'topic' 

# Список очередей
QUEUES = [
    'email_queue',
    'db_log_queue',
    'excel_report_queue',
    'console_monitor_queue',
    'critical_alert_queue',
    'analytics_queue',
    'pdf_ticket_queue',
    'slack_notify_queue',
]

# Правила маршрутизации: { 'routing_key': [список_очередей] }
BINDINGS = {
    'event.registered.#': [
        'email_queue',
        'db_log_queue',
        'excel_report_queue',
        'pdf_ticket_queue',
    ],
    'event.#': [
        'console_monitor_queue',
        'analytics_queue',
    ],
    'event.registered.vip': [
        'critical_alert_queue',
        'slack_notify_queue',
    ],
}

def wait_for_rabbitmq(max_retries: int = 15, retry_delay: int = 3):
    """Ждёт, пока RabbitMQ станет доступен."""
    for attempt in range(1, max_retries + 1):
        try:
            credentials = pika.PlainCredentials(USER, PASSWORD)
            parameters = pika.ConnectionParameters(
                host=HOST, 
                port=PORT, 
                credentials=credentials,
                # Добавляем таймауты для быстрого определения ошибки
                connection_attempts=1,
                socket_timeout=5
            )
            connection = pika.BlockingConnection(parameters)
            connection.close()
            print(f"✅ RabbitMQ доступен на {HOST}:{PORT}")
            return
        except pika.exceptions.AMQPConnectionError as e:
            print(f"⏳ Ожидание RabbitMQ (попытка {attempt}/{max_retries})...")
            print(f"   Ошибка: {e}")
            time.sleep(retry_delay)
        except Exception as e:
            print(f"⏳ Ошибка подключения (попытка {attempt}/{max_retries}): {e}")
            time.sleep(retry_delay)

    print(f"❌ RabbitMQ не доступен после {max_retries} попыток")
    print(f"   Пробовали подключиться к {HOST}:{PORT}")
    sys.exit(1)

def setup_infrastructure():
    """Подключается к RabbitMQ и создаёт всю инфраструктуру."""
    print(f"🔧 Начинаем настройку инфраструктуры для RabbitMQ на {HOST}:{PORT}")
    wait_for_rabbitmq()
    
    credentials = pika.PlainCredentials(USER, PASSWORD)
    parameters = pika.ConnectionParameters(
        host=HOST,
        port=PORT,
        credentials=credentials,
    )
    
    try:
        connection = pika.BlockingConnection(parameters)
        channel = connection.channel()
        print("✅ Подключено к RabbitMQ")
        
        # 2. Создаём Exchange (обменник)
        channel.exchange_declare(
            exchange=EXCHANGE_NAME,
            exchange_type=EXCHANGE_TYPE,
            durable=True
        )
        print(f"✅ Exchange '{EXCHANGE_NAME}' создан")
        
        # 3. Создаём очереди
        for queue_name in QUEUES:
            channel.queue_declare(
                queue=queue_name,
                durable=True,
                auto_delete=False
            )
            print(f"✅ Очередь '{queue_name}' создана")
        
        # 4. Создаём связки (bindings)
        for routing_key, queue_list in BINDINGS.items():
            for queue_name in queue_list:
                channel.queue_bind(
                    exchange=EXCHANGE_NAME,
                    queue=queue_name,
                    routing_key=routing_key
                )
                print(f"✅ Binding: '{routing_key}' → '{queue_name}'")
        
        print("\n🎉 Инфраструктура готова! Можно запускать сервисы.")
        
        return connection
        
    except pika.exceptions.AMQPConnectionError as e:
        print(f"❌ Ошибка: Не удалось подключиться к RabbitMQ: {e}", file=sys.stderr)
        print(f"   Проверьте что RabbitMQ запущен на {HOST}:{PORT}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"❌ Ошибка при настройке: {e}", file=sys.stderr)
        sys.exit(1)

def keep_alive():
    """Держит сервис запущенным после настройки инфраструктуры."""
    print("🔄 Orchestrator перешёл в режим ожидания. Инфраструктура настроена.")
    try:
        while True:
            time.sleep(60)
    except KeyboardInterrupt:
       print("🛑 Orchestrator остановлен")

if __name__ == '__main__':
    setup_infrastructure()
    keep_alive()