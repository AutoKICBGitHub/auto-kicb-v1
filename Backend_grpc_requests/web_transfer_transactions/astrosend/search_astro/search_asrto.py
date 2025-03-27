#!/usr/bin/env python
# -*- coding: utf-8 -*-

import grpc
import json
import time
import uuid
import os
import sys
from google.protobuf.json_format import ParseDict

# Импортируем скомпилированные протофайлы
import astrasend_internal_api_pb2 as pb2
import astrasend_internal_api_pb2_grpc as pb2_grpc

def generate_ref_id():
    """Генерирует уникальный refid для запроса"""
    return f"REF{int(time.time())}{str(uuid.uuid4()).replace('-', '')[:12]}"

def send_search_request(test_case, host="localhost", port=5438):
    """Отправляет запрос на поиск перевода и проверяет результат"""
    try:
        # Создаем канал и клиент
        with grpc.insecure_channel(f"{host}:{port}") as channel:
            stub = pb2_grpc.AstrasendInternalApiStub(channel)
            
            # Создаем запрос из JSON данных
            request = pb2.SearchReceiveMoneyRequest()
            ParseDict(test_case["data"], request)
            
            # Отправляем запрос с уникальным refId
            metadata = [('refid', generate_ref_id())]
            response = stub.searchReceiveMoney(request, metadata=metadata)
            
            # Проверяем результат
            success = response.success
            expected = test_case["expected_success"]
            result = "ПРОЙДЕН" if success == expected else "НЕ ПРОЙДЕН"
            
            # Формируем детали ответа
            if success:
                details = f"Найден перевод: {response.data.mtcn if hasattr(response.data, 'mtcn') else 'Данные получены'}"
            else:
                details = f"Ошибка: {response.error.code}, Данные: {response.error.data}"
            
            return {
                "test_name": test_case["name"],
                "result": result,
                "expected": expected,
                "actual": success,
                "details": details
            }
    except Exception as e:
        return {
            "test_name": test_case["name"],
            "result": "ОШИБКА",
            "expected": test_case["expected_success"],
            "actual": "Exception",
            "details": str(e)
        }

def run_tests(test_cases_file, host="localhost", port=5438):
    """Запускает все тесты из файла"""
    # Загружаем тестовые кейсы
    with open(test_cases_file, 'r', encoding='utf-8') as f:
        test_cases = json.load(f)["test_cases"]
    
    # Запускаем каждый тест
    results = []
    for i, test_case in enumerate(test_cases):
        print(f"\n[{i+1}/{len(test_cases)}] Тест: {test_case['name']}")
        print(f"Описание: {test_case['description']}")
        
        # Отправляем запрос и получаем результат
        result = send_search_request(test_case, host, port)
        results.append(result)
        
        # Выводим результат
        print(f"Результат: {result['result']}")
        print(f"Ожидалось: {result['expected']}, Получено: {result['actual']}")
        print(f"Детали: {result['details']}")
        
        # Пауза между запросами
        if i < len(test_cases) - 1:
            time.sleep(1)
    
    # Подсчитываем статистику
    passed = sum(1 for r in results if r["result"] == "ПРОЙДЕН")
    failed = sum(1 for r in results if r["result"] == "НЕ ПРОЙДЕН")
    errors = sum(1 for r in results if r["result"] == "ОШИБКА")
    
    # Выводим общий результат
    print(f"\n=== ИТОГОВЫЕ РЕЗУЛЬТАТЫ ===")
    print(f"Всего тестов: {len(results)}")
    print(f"Пройдено: {passed}")
    print(f"Не пройдено: {failed}")
    print(f"Ошибки: {errors}")
    
    # Выводим детали по непройденным тестам
    if failed > 0 or errors > 0:
        print("\nДетали по непройденным тестам:")
        for result in results:
            if result["result"] != "ПРОЙДЕН":
                print(f"- {result['test_name']}: {result['details']}")
    
    # Сохраняем результаты в файл
    results_file = os.path.join(os.path.dirname(test_cases_file), "search_results.json")
    with open(results_file, 'w', encoding='utf-8') as f:
        json.dump({
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "total": len(results),
            "passed": passed,
            "failed": failed,
            "errors": errors,
            "results": results
        }, f, indent=2, ensure_ascii=False)
    
    print(f"\nРезультаты сохранены в файл: {results_file}")
    return passed, failed, errors

def main():
    """Основная функция"""
    # Получаем аргументы командной строки
    import argparse
    parser = argparse.ArgumentParser(description='Запуск тестов поиска переводов AstrasendInternalApi')
    parser.add_argument('--host', default='localhost', help='Хост сервера')
    parser.add_argument('--port', type=int, default=5438, help='Порт сервера')
    parser.add_argument('--file', default='search_test_cases.json', help='Файл с тестовыми кейсами')
    args = parser.parse_args()
    
    # Проверяем наличие файла с тестами
    test_cases_file = args.file
    if not os.path.isfile(test_cases_file):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        test_cases_file = os.path.join(current_dir, args.file)
        if not os.path.isfile(test_cases_file):
            print(f"Ошибка: Файл с тестовыми кейсами не найден: {args.file}")
            sys.exit(1)
    
    # Запускаем тесты
    print(f"Запуск тестов из файла: {test_cases_file}")
    print(f"Сервер: {args.host}:{args.port}")
    
    passed, failed, errors = run_tests(test_cases_file, args.host, args.port)
    
    # Возвращаем код ошибки, если есть непройденные тесты
    sys.exit(1 if failed > 0 or errors > 0 else 0)

if __name__ == "__main__":
    main()
