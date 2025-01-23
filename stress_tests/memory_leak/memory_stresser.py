import grpc
import time
import psutil
import os
import sys
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from datetime import datetime
from collections import defaultdict

# Добавляем путь к директории, где находится протофайл
sys.path.append(os.path.abspath("C:\\project_kicb\\stress_tests\\memory_leak"))

from protofile_pb2_grpc import WebDirectoryApiStub
from protofile_pb2 import IncomingWebDirectory  # Изменяем на правильный класс запроса

class MemoryStresser:
    def __init__(self, config_path='directory_config.json'):
        # Используем secure channel для подключения к тестовому серверу
        self.channel = grpc.secure_channel(
            'newibanktest.kicb.net:443', 
            grpc.ssl_channel_credentials()
        )
        self.stub = WebDirectoryApiStub(self.channel)
        self.process = psutil.Process(os.getpid())
        
        # Загружаем конфигурацию справочников
        config_file = Path(__file__).parent / config_path
        with open(config_file, 'r', encoding='utf-8') as f:
            self.directory_config = json.load(f)
        
    def get_memory_usage(self):
        """Возвращает текущее потребление памяти в мегабайтах"""
        return self.process.memory_info().rss / 1024 / 1024  # Конвертируем байты в мегабайты
        
    def get_directory(self, directory_name):
        """Выполняет запрос на получение справочника"""
        try:
            metadata = (
                ('sessionkey', '4PAvqwIl7PY9XxvzRIawvV'),
            )
            
            request_data = {
                "dataVersion": 1
            }
            
            request = IncomingWebDirectory(
                code=directory_name,
                data=json.dumps(request_data)
            )
            
            print(f"\nОтправляем запрос: {directory_name}")
            
            response = self.stub.makeWebDirectory(request, metadata=metadata)
            
            if response.success:
                print(f"Успешный ответ для {directory_name}")
                return {
                    "success": True,
                    "error": None
                }
            else:
                error_code = response.error.code if response.error else "UNKNOWN_ERROR"
                print(f"Ошибка для {directory_name}: {error_code}")
                return {
                    "success": False,
                    "error": error_code
                }
            
        except grpc.RpcError as e:
            error = str(e.code()) if hasattr(e, 'code') else str(e)
            print(f"Ошибка при запросе {directory_name}: {error}")
            return {
                "success": False,
                "error": error
            }

    def run_stress_test(self, num_requests=100, concurrent_requests=20, batch_size=20):
        """Запускает стресс-тест"""
        print(f"Начало стресс-теста: {num_requests} запросов")
        
        metadata = (
            ('sessionkey', '4PAvqwIl7PY9XxvzRIawvV'),
        )
        
        request_data = {
            "dataVersion": 1
        }
        
        request = IncomingWebDirectory(
            code=self.directory_config[0],
            data=json.dumps(request_data)
        )
        
        print("Начинаем отправку запросов...")
        
        futures = []
        processed = set()  # Множество для отслеживания обработанных запросов
        
        # Отправляем запросы
        for i in range(num_requests):
            try:
                future = self.stub.makeWebDirectory.future(request, metadata=metadata)
                futures.append((i, future))
            except Exception as e:
                print(f"Ошибка при отправке запроса #{i}: {str(e)}")
        
        # Проверяем завершенные запросы
        completed = 0
        success = 0
        errors = 0
        
        while completed < len(futures):
            for i, future in futures:
                if i not in processed and future.done():
                    completed += 1
                    processed.add(i)  # Отмечаем запрос как обработанный
                    
                    try:
                        response = future.result()
                        if response.success:
                            success += 1
                            print(f"✅ Запрос #{i} успешно выполнен")
                        else:
                            errors += 1
                            error_code = response.error.code if response.error else "UNKNOWN_ERROR"
                            print(f"❌ Запрос #{i} завершился с ошибкой: {error_code}")
                    except Exception as e:
                        errors += 1
                        print(f"❌ Запрос #{i} завершился с исключением: {str(e)}")
                    
                    # Выводим текущую статистику
                    print(f"\nСтатистика: Отправлено: {len(futures)}, Завершено: {completed}, Успешно: {success}, Ошибок: {errors}")
            
            time.sleep(0.1)
        
        print(f"\nТест завершен. Итоговая статистика:")
        print(f"Всего запросов: {len(futures)}")
        print(f"Успешных: {success}")
        print(f"Ошибок: {errors}")

if __name__ == "__main__":
    stresser = MemoryStresser()
    stresser.run_stress_test(
        num_requests=100,
        concurrent_requests=1,  # Не используется
        batch_size=1           # Не используется
    )
