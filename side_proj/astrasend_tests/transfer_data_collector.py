import json
import psycopg2
from psycopg2.extras import RealDictCursor
from typing import Dict, Any, List
from dataclasses import dataclass
from decimal import Decimal

@dataclass
class DatabaseConfig:
    user: str = "postgres"
    password: str = "postgres"
    host: str = "localhost"
    port: str = "5434"
    database: str = "ibank"

class TransferDataCollector:
    def __init__(self, config: DatabaseConfig):
        self.config = config

    def connect(self) -> psycopg2.extensions.connection:
        return psycopg2.connect(
            user=self.config.user,
            password=self.config.password,
            host=self.config.host,
            port=self.config.port,
            database=self.config.database
        )

    def load_config(self, json_file_path: str = "C:/project_kicb/side_proj/astrasend_tests/transfer_data.json") -> Dict:
        """Загружает конфигурацию из JSON файла"""
        with open(json_file_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def save_data(self, data: Dict, json_file_path: str = "C:/project_kicb/side_proj/astrasend_tests/transfer_data.json"):
        """Сохраняет данные в JSON файл"""
        config = self.load_config(json_file_path)
        config['data'] = data
        with open(json_file_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=4)

    def decimal_default(self, obj):
        """Конвертирует Decimal в float для JSON сериализации"""
        if isinstance(obj, Decimal):
            return float(obj)
        raise TypeError

    def fetch_accounts(self, customer_no: str, conn) -> List[Dict]:
        """Получает список всех счетов клиента"""
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                SELECT 
                    id as account_id,
                    ccy,
                    acy_withdrawable_bal as balance
                FROM accounts 
                WHERE customer_no = %s 
                AND acy_withdrawable_bal > 500
                ORDER BY id
            """, (customer_no,))
            accounts = cur.fetchall()
            # Конвертируем Decimal в float
            for account in accounts:
                if isinstance(account['balance'], Decimal):
                    account['balance'] = float(account['balance'])
            return accounts

    def fetch_transfer_data(self, json_file_path: str = "C:/project_kicb/side_proj/astrasend_tests/transfer_data.json") -> str:
        """
        Получает данные для трансфера и сохраняет в JSON файл
        
        Args:
            json_file_path: путь к JSON файлу для сохранения
            
        Returns:
            str: JSON строка с данными для трансфера
        """
        try:
            config = self.load_config(json_file_path)
            customer_no = config['customer_no']
            selected_index = config.get('selected_account_index', 0)
            
            with self.connect() as conn:
                # Получаем список всех счетов
                accounts = self.fetch_accounts(customer_no, conn)
                
                if not accounts:
                    raise Exception(f"Не найдены счета для customer_no: {customer_no}")
                
                # Сохраняем список счетов в конфиг
                config['available_accounts'] = accounts
                
                # Проверяем валидность индекса
                if selected_index >= len(accounts):
                    selected_index = 0
                    config['selected_account_index'] = 0
                
                # Выбираем нужный счет
                selected_account = accounts[selected_index]
                
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                    # Получаем user_id
                    cur.execute("""
                        SELECT id 
                        FROM users 
                        WHERE customer_no = %s 
                        LIMIT 1
                    """, (customer_no,))
                    user_result = cur.fetchone()
                    user_id = user_result['id']

                    # Получаем session_key
                    cur.execute("""
                        SELECT session_key
                        FROM sessions 
                        WHERE user_id = %s AND is_valid = true
                        LIMIT 1
                    """, (user_id,))
                    session_result = cur.fetchone()
                    
                    # Получаем имя получателя
                    cur.execute("""
                        SELECT full_name_lat
                        FROM customers 
                        WHERE customer_no = %s
                    """, (customer_no,))
                    name_result = cur.fetchone()
                    full_name = name_result['full_name_lat'].split()
                    
                    result = {
                        "sessionKey": session_result['session_key'] if session_result else "",
                        "creditCcy": selected_account['ccy'],
                        "accountIdDebit": selected_account['account_id'],
                        "recipientFirstName": full_name[0] if full_name else "",
                        "recipientLastName": full_name[1] if len(full_name) > 1 else "",
                        "propValue": config['data']['propValue']
                    }
                    
                    # Сохраняем все изменения в конфиг
                    config['data'] = result
                    with open(json_file_path, 'w', encoding='utf-8') as f:
                        json.dump(config, f, ensure_ascii=False, indent=4)
                    
                    return json.dumps(result, ensure_ascii=False, indent=4)
        except Exception as e:
            raise Exception(f"Ошибка при получении данных: {str(e)}")

# Пример использования:
if __name__ == "__main__":
    config = DatabaseConfig()
    collector = TransferDataCollector(config)
    json_data = collector.fetch_transfer_data()
    print(json_data)
