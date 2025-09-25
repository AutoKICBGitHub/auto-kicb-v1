import json
import re
from datetime import datetime
import os

class LogAnalyzer:
    def __init__(self, log_file_path):
        self.log_file_path = log_file_path
        
    def _parse_log_line(self, line):
        """Парсит строку лога и извлекает timestamp, traceId и данные"""
        # Паттерны для парсинга
        timestamp_pattern = r'\[(\d{4}-\d{2}-\d{2}\s\d{2}:\d{2}:\d{2})'
        trace_pattern = r'traceId:\s*["\']?([\w:-]+)["\']?'
        method_pattern = r'Method\s+([\w.]+)\s+was called'
        response_pattern = r'Method\s+([\w.]+)\s+with response data\s+({.*})\s+completed'
        
        timestamp_match = re.search(timestamp_pattern, line)
        trace_match = re.search(trace_pattern, line)
        method_match = re.search(method_pattern, line)
        response_match = re.search(response_pattern, line)
        
        # Пытаемся распарсить JSON из ответа
        response_data = None
        if response_match:
            try:
                json_str = response_match.group(2)
                response_data = json.loads(json_str)
            except:
                response_data = None
        
        return {
            'timestamp': timestamp_match.group(1) if timestamp_match else None,
            'trace_id': trace_match.group(1) if trace_match else None,
            'method': method_match.group(1) if method_match else None,
            'response_data': response_data,
            'content': line.strip()
        }

    def analyze_operation(self, trace_id, context_lines=50):
        """
        Анализирует операцию по её trace_id
        
        Args:
            trace_id: Trace ID операции для анализа
            context_lines: Количество строк до и после для контекста
        """
        if not os.path.exists(self.log_file_path):
            print(f"Файл логов не найден: {self.log_file_path}")
            return
            
        print(f"\nАнализ операции с Trace ID: {trace_id}")
        print("=" * 80)
        
        # Читаем лог и ищем строки с нужным trace_id
        matching_lines = []
        with open(self.log_file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            
        for i, line in enumerate(lines):
            if trace_id in line:
                # Собираем контекст
                start = max(0, i - context_lines)
                end = min(len(lines), i + context_lines + 1)
                
                for j in range(start, end):
                    parsed = self._parse_log_line(lines[j])
                    if parsed['timestamp']:
                        matching_lines.append(parsed)
        
        if not matching_lines:
            print(f"Операция с Trace ID {trace_id} не найдена в логах")
            return
            
        # Анализируем найденные строки
        print(f"Найдено {len(matching_lines)} релевантных записей\n")
        
        # Группируем события по методам
        methods = {}
        for entry in matching_lines:
            if entry['method']:
                if entry['method'] not in methods:
                    methods[entry['method']] = []
                methods[entry['method']].append(entry)
        
        # Анализируем каждый метод
        for method, entries in methods.items():
            print(f"\nМетод: {method}")
            print("-" * 40)
            
            for entry in entries:
                print(f"[{entry['timestamp']}] {entry['trace_id']}")
                if entry['response_data']:
                    success = entry['response_data'].get('success')
                    error = entry['response_data'].get('error')
                    data = entry['response_data'].get('data')
                    
                    print(f"Статус: {'Успешно' if success else 'Ошибка'}")
                    if error:
                        print(f"Ошибка: {error}")
                    if data:
                        if isinstance(data, dict):
                            for key, value in data.items():
                                print(f"{key}: {value}")
                        else:
                            print(f"Данные: {data}")
                print()
        
        # Общая статистика
        print("\nОбщая статистика:")
        print("-" * 40)
        print(f"Всего методов: {len(methods)}")
        print(f"Всего запросов: {len(matching_lines)}")
        
        # Проверяем успешность операции
        success_responses = [
            entry for entry in matching_lines 
            if entry['response_data'] and entry['response_data'].get('success')
        ]
        error_responses = [
            entry for entry in matching_lines 
            if entry['response_data'] and entry['response_data'].get('error')
        ]
        
        print(f"Успешных ответов: {len(success_responses)}")
        if error_responses:
            print("\nНайдены ошибки:")
            for error in error_responses:
                print(f"[{error['timestamp']}] {error['response_data']['error']}")

    def analyze_last_operations(self, count=5):
        """Анализирует последние N операций"""
        if not os.path.exists(self.log_file_path):
            print(f"Файл логов не найден: {self.log_file_path}")
            return
            
        operations = set()
        with open(self.log_file_path, 'r', encoding='utf-8') as f:
            for line in f:
                operation_id_match = re.search(r'operation_id[=:]\s*["\']?([\w-]+)["\']?', line)
                if operation_id_match:
                    operations.add(operation_id_match.group(1))
        
        last_operations = list(operations)[-count:]
        
        print(f"\nАнализ последних {count} операций:")
        print("=" * 80)
        
        for op_id in last_operations:
            self.analyze_operation(op_id, context_lines=20)
            print("\n" + "=" * 80)

def main():
    import argparse
    parser = argparse.ArgumentParser(description='Анализ логов сервиса')
    parser.add_argument('--log-file', required=True, help='Путь к файлу логов')
    parser.add_argument('--operation-id', help='ID операции для анализа')
    parser.add_argument('--last', type=int, default=5, help='Количество последних операций для анализа')
    
    args = parser.parse_args()
    
    analyzer = LogAnalyzer(args.log_file)
    
    if args.operation_id:
        analyzer.analyze_operation(args.operation_id)
    else:
        analyzer.analyze_last_operations(args.last)

if __name__ == "__main__":
    main()
