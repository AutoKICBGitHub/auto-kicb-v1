import json
import os
from datetime import datetime
from logger import TransferLogger

def print_separator():
    print("\n" + "="*50 + "\n")

def view_transfer_data():
    """Показывает текущие данные из transfer_data.json"""
    try:
        with open('transfer_data.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
            print("Текущие данные перевода:")
            print_separator()
            print("Customer No:", data.get('customer_no'))
            
            print("\nДоступные счета:")
            for idx, account in enumerate(data.get('available_accounts', [])):
                print(f"{idx}. ID: {account['account_id']}, "
                      f"Валюта: {account['ccy']}, "
                      f"Баланс: {account['balance']}")
            
            print(f"\nВыбранный счет (индекс {data.get('selected_account_index', 0)}):")
            print(json.dumps(data.get('data', {}), indent=2, ensure_ascii=False))
    except Exception as e:
        print(f"Ошибка при чтении transfer_data.json: {str(e)}")

def view_logs(date=None, operation_id=None):
    """Показывает логи операций"""
    logger = TransferLogger()
    
    if date is None:
        date = datetime.now().strftime("%Y%m%d")
    
    logs = logger.get_transfer_logs(operation_id=operation_id, date=date)
    
    if not logs:
        print(f"Логи не найдены для даты {date}" + 
              (f" и operation_id {operation_id}" if operation_id else ""))
        return
    
    print(f"Найдено записей: {len(logs)}")
    print_separator()
    
    for idx, log in enumerate(logs, 1):
        print(f"Запись {idx}:")
        print(f"Время: {log['timestamp']}")
        print(f"Operation ID: {log['operation_id']}")
        print(f"Статус: {log['status']}")
        
        print("\nЗапрос:")
        print(json.dumps(log['request'], indent=2, ensure_ascii=False))
        
        print("\nОтвет:")
        print(json.dumps(log['response'], indent=2, ensure_ascii=False))
        print_separator()

def main():
    print("Просмотр результатов тестирования\n")
    
    while True:
        print("\nВыберите действие:")
        print("1. Посмотреть текущие данные перевода")
        print("2. Посмотреть логи за сегодня")
        print("3. Посмотреть логи за конкретную дату")
        print("4. Найти логи по ID операции")
        print("5. Выход")
        
        choice = input("\nВаш выбор: ")
        
        if choice == "1":
            print_separator()
            view_transfer_data()
        
        elif choice == "2":
            print_separator()
            view_logs()
        
        elif choice == "3":
            date = input("Введите дату в формате YYYYMMDD: ")
            print_separator()
            view_logs(date=date)
        
        elif choice == "4":
            operation_id = input("Введите ID операции: ")
            print_separator()
            view_logs(operation_id=operation_id)
        
        elif choice == "5":
            break
        
        else:
            print("Неверный выбор. Попробуйте снова.")

if __name__ == "__main__":
    main()
