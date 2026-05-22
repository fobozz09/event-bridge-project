# test_api_gateway.py
import requests
import json
import time
import os
from typing import Dict, Any

API_GATEWAY_HOST = os.getenv('API_GATEWAY_HOST', 'api_gateway')
API_GATEWAY_PORT = os.getenv('API_GATEWAY_PORT', '8000')
API_GATEWAY_URL = f"http://{API_GATEWAY_HOST}:{API_GATEWAY_PORT}"

def send_test_requests_to_api_gateway():
    """Отправляет 5 разных тестовых запросов к API Gateway"""
    
    print("\n" + "="*60)
    print("🧪 ЗАПУСК ТЕСТОВ API GATEWAY")
    print("="*60)
    
    test_scenarios = [
        {
            "name": "Тест 1: Регистрация обычного пользователя",
            "endpoint": "/api/register",
            "method": "POST",
            "data": {
                "user_name": "John Doe",
                "user_email": "john@example.com",
                "event_name": "Tech Conference 2025",
                "is_vip": False
            }
        },
        {
            "name": "Тест 2: VIP регистрация пользователя",
            "endpoint": "/api/register",
            "method": "POST",
            "data": {
                "user_name": "Sarah Connor",
                "user_email": "sarah.connor@example.com",
                "event_name": "AI Summit 2026",
                "is_vip": True
            }
        },
        {
            "name": "Тест 3: Получение всех событий",
            "endpoint": "/api/events",
            "method": "GET",
            "data": None
        },
        {
            "name": "Тест 4: Статус сервиса",
            "endpoint": "/health",
            "method": "GET",
            "data": None
        },
        {
            "name": "Тест 5: VIP дашборд",
            "endpoint": "/api/vip/dashboard",
            "method": "GET",
            "data": None
        }
    ]
    
    results = []
    
    for i, test in enumerate(test_scenarios, 1):
        print(f"\n📤 {test['name']}")
        print(f"   → {test['method']} {API_GATEWAY_URL}{test['endpoint']}")
        
        try:
            if test['method'] == 'POST':
                response = requests.post(
                    f"{API_GATEWAY_URL}{test['endpoint']}",
                    json=test['data'],
                    timeout=5
                )
            else:  # GET
                response = requests.get(
                    f"{API_GATEWAY_URL}{test['endpoint']}",
                    timeout=5
                )
            
            print(f"   ✅ Статус: {response.status_code}")
            print(f"   📦 Ответ: {response.json() if response.text else 'No content'}")
            results.append({"test": test['name'], "status": "PASS", "code": response.status_code})
            
        except requests.exceptions.ConnectionError:
            print(f"   ❌ Ошибка: Не удалось подключиться к API Gateway (порт {API_GATEWAY_PORT})")
            results.append({"test": test['name'], "status": "FAIL", "error": "Connection refused"})
            
        except requests.exceptions.Timeout:
            print(f"   ❌ Ошибка: Таймаут ожидания ответа")
            results.append({"test": test['name'], "status": "FAIL", "error": "Timeout"})
            
        except Exception as e:
            print(f"   ❌ Ошибка: {str(e)}")
            results.append({"test": test['name'], "status": "FAIL", "error": str(e)})
        
        # Небольшая пауза между запросами
        time.sleep(0.5)
    
    # Выводим итоговый отчет
    print("\n" + "="*60)
    print("📊 ИТОГИ ТЕСТИРОВАНИЯ")
    print("="*60)
    
    passed = sum(1 for r in results if r['status'] == 'PASS')
    failed = len(results) - passed
    
    for r in results:
        status_icon = "✅" if r['status'] == 'PASS' else "❌"
        print(f"{status_icon} {r['test']}: {r['status']}")
    
    print(f"\n📈 Всего: {passed}/{len(results)} тестов пройдено")
    
    if failed > 0:
        print("⚠️ ВНИМАНИЕ: Некоторые тесты не прошли! API Gateway может быть недоступен.")
    else:
        print("🎉 ОТЛИЧНО! Все тесты успешно пройдены!")
    
    print("="*60 + "\n")
    
    return passed == len(results)

if __name__ == "__main__":
    # Ждем немного, чтобы сервисы успели запуститься
    time.sleep(3)
    send_test_requests_to_api_gateway()