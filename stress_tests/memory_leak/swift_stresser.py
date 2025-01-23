import grpc
import time
import psutil
import os
import sys
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from datetime import datetime

# Добавляем путь к директории с протофайлом
sys.path.append(os.path.abspath("C:\\project_kicb\\stress_tests\\memory_leak"))

from protofile_pb2_grpc import WebDirectoryApiStub
from protofile_pb2 import IncomingWebDirectory

class SwiftStresser:
    def __init__(self, config_path='swift_config.json'):
        # Используем secure channel для подключения к тестовому серверу
        self.channel = grpc.secure_channel(
            'newibanktest.kicb.net:443', 
            grpc.ssl_channel_credentials()
        )
        self.stub = WebDirectoryApiStub(self.channel)
        self.process = psutil.Process(os.getpid())
        
        # Загружаем конфигурацию SWIFT кодов
        config_file = Path(__file__).parent / config_path
        with open(config_file, 'r', encoding='utf-8') as f:
            self.swift_codes = json.load(f)
        
    def get_memory_usage(self):
        """Возвращает текущее потребление памяти в мегабайтах"""
        return self.process.memory_info().rss / 1024 / 1024
        
    def run_stress_test(self, num_requests=100):
        """Запускает стресс-тест"""
        print(f"Начало стресс-теста SWIFT: {num_requests} запросов")
        
        metadata = (
            ('sessionkey', '4PAvqwIl7PY9XxvzRIawvV'),
            ('device-type', 'browser')
        )
        
        futures = []
        processed = set()
        
        # Отправляем запросы, циклически используя разные SWIFT коды
        for i in range(num_requests):
            try:
                # Выбираем SWIFT код по кругу
                swift_code = self.swift_codes[i % len(self.swift_codes)]
                
                request_data = {
                    "propValue": swift_code,
                    "propType": "name"
                }
                
                request = IncomingWebDirectory(
                    code="GET_DATA_BY_SWIFT_CODE",
                    data=json.dumps(request_data)
                )
                
                future = self.stub.makeWebDirectory.future(request, metadata=metadata)
                futures.append((i, future, swift_code))  # Сохраняем использованный код
            except Exception as e:
                print(f"Ошибка при отправке запроса #{i}: {str(e)}")
        
        # Проверяем завершенные запросы
        completed = 0
        success = 0
        errors = 0
        
        while completed < len(futures):
            for i, future, swift_code in futures:
                if i not in processed and future.done():
                    completed += 1
                    processed.add(i)
                    
                    try:
                        response = future.result()
                        print(f"\n=== SWIFT запрос #{i} (код: {swift_code}) ===")
                        print(f"Тип ответа: {type(response)}")
                        print(f"Все атрибуты ответа: {dir(response)}")
                        print(f"Сырой ответ: {response}")
                        
                        # Пробуем вывести все возможные поля
                        for field in dir(response):
                            if not field.startswith('_'):  # Пропускаем внутренние атрибуты
                                try:
                                    value = getattr(response, field)
                                    print(f"{field}: {value}")
                                except Exception as field_error:
                                    print(f"Ошибка при получении поля {field}: {field_error}")
                        
                        if hasattr(response, 'success'):
                            if response.success:
                                success += 1
                                print("✅ Запрос успешен")
                            else:
                                errors += 1
                                print("❌ Запрос завершился с ошибкой")
                        
                        if hasattr(response, 'data') and response.data:
                            try:
                                data = json.loads(response.data)
                                print("\nДанные ответа:")
                                print(json.dumps(data, indent=2, ensure_ascii=False))
                            except json.JSONDecodeError:
                                print("\nСырые данные:")
                                print(response.data)
                        
                    except Exception as e:
                        errors += 1
                        print(f"\n❌ SWIFT запрос #{i} (код: {swift_code}) завершился с исключением:")
                        print(f"Тип исключения: {type(e)}")
                        print(f"Текст исключения: {str(e)}")
                        print(f"Атрибуты исключения: {dir(e)}")
                        
                        if hasattr(e, '_state'):
                            print(f"Состояние: {e._state}")
                        if hasattr(e, 'code'):
                            print(f"Код ошибки: {e.code()}")
                        if hasattr(e, 'details'):
                            print(f"Детали: {e.details()}")
                    
                    print(f"\nСтатистика SWIFT: Отправлено: {len(futures)}, Завершено: {completed}, Успешно: {success}, Ошибок: {errors}")
            
            time.sleep(0.1)
        
        print(f"\nТест SWIFT завершен. Итоговая статистика:")
        print(f"Всего запросов: {len(futures)}")
        print(f"Успешных: {success}")
        print(f"Ошибок: {errors}")

if __name__ == "__main__":
    stresser = SwiftStresser()
    stresser.run_stress_test(num_requests=1) 