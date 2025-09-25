import json
import os
from transfer_data_collector import TransferDataCollector, DatabaseConfig
from astrosend_new import execute_astrosend_payment
from logger import TransferLogger
from log_analyzer import LogAnalyzer
from datetime import datetime

def print_separator():
    print("\n" + "="*50 + "\n")

def main():
    print("Начало тестирования Astrosend\n")
    print_separator()
    
    # 1. Получаем данные из БД
    print("1. Получение данных из базы данных")
    try:
        config = DatabaseConfig()
        collector = TransferDataCollector(config)
        json_data = collector.fetch_transfer_data()
        
        # Читаем сохраненные данные
        with open('C:/project_kicb/side_proj/astrasend_tests/transfer_data.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
            print("✓ Данные успешно получены и сохранены в transfer_data.json")
            print("\nДоступные счета:")
            for idx, account in enumerate(data.get('available_accounts', [])):
                print(f"{idx}. ID: {account['account_id']}, Валюта: {account['ccy']}, Баланс: {account['balance']}")
            print(f"\nВыбран счет с индексом: {data.get('selected_account_index', 0)}")
    except Exception as e:
        print(f"❌ Ошибка при получении данных: {str(e)}")
        return
    
    print_separator()
    
    # 2. Выполняем перевод
    print("2. Выполнение перевода Astrosend")
    try:
        result = execute_astrosend_payment()
        print("✓ Перевод успешно выполнен")
        print("\nДетали операции:")
        print(f"Operation ID: {result['operation_id']}")
        
        # Получаем данные ответов
        payment_data = json.loads(result['payment_response'].data) if hasattr(result['payment_response'], 'data') else {}
        confirm_data = json.loads(result['confirm_response'].data) if hasattr(result['confirm_response'], 'data') else {}
        
        print("\nДанные создания платежа:")
        print(json.dumps(payment_data, indent=2, ensure_ascii=False))
        print("\nДанные подтверждения платежа:")
        print(json.dumps(confirm_data, indent=2, ensure_ascii=False))
    except Exception as e:
        print(f"❌ Ошибка при выполнении перевода: {str(e)}")
        return
    
    print_separator()
    
    # 3. Показываем логи операции
    print("3. Логи операции")
    try:
        logger = TransferLogger()
        logs = logger.get_transfer_logs(operation_id=result['operation_id'])
        print(f"Найдено записей в логах: {len(logs)}")
        print("\nПодробные логи:")
        print(json.dumps(logs, indent=4, ensure_ascii=False))
    except Exception as e:
        print(f"❌ Ошибка при получении логов: {str(e)}")
    
    print_separator()
    
    # 4. Анализ логов сервиса
    print("4. Анализ логов сервиса")
    try:
        service_log_path = input("\nВведите путь к файлу логов сервиса: ").strip()
        if os.path.exists(service_log_path):
            analyzer = LogAnalyzer(service_log_path)
            analyzer.analyze_operation(result["operation_id"])
        else:
            print(f"Файл логов не найден: {service_log_path}")
    except Exception as e:
        print(f"Ошибка при анализе логов: {str(e)}")
    
    print_separator()
    print("Тестирование завершено!")

if __name__ == "__main__":
    main()
