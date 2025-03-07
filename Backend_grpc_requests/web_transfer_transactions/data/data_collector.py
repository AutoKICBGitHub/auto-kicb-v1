import json
import psycopg2
from psycopg2.extras import RealDictCursor
from typing import Dict, Any, List
from dataclasses import dataclass

@dataclass
class DatabaseConfig:
    user: str = "postgres"
    password: str = "postgres"
    host: str = "localhost"
    port: str = "5434"
    database: str = "ibank"

class DataCollector:
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

    def fetch_sessions_to_json(self, user_id: int, json_file_path: str = "C:/project_kicb/Backend_grpc_requests/web_transfer_transactions/data/session_data.json") -> str:
        """
        Получает первую активную сессию пользователя и сохраняет в JSON файл
        
        Args:
            user_id: ID пользователя
            json_file_path: путь к JSON файлу для сохранения
            
        Returns:
            str: JSON строка с данными сессии
        """
        try:
            with self.connect() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                    cur.execute("""
                        SELECT session_key, session_id
                        FROM sessions 
                        WHERE user_id = 134 AND is_valid = true
                        LIMIT 1
                    """, (user_id,))
                    result = cur.fetchone()
                    json_data = json.dumps(result, ensure_ascii=False, indent=4)
                    
                    # Сохраняем результат в JSON файл
                    with open(json_file_path, 'w', encoding='utf-8') as f:
                        f.write(json_data)
                    
                    return json_data
        except Exception as e:
            raise Exception(f"Ошибка при получении данных: {str(e)}")

# Пример использования:
if __name__ == "__main__":
    config = DatabaseConfig()
    collector = DataCollector(config)
    json_data = collector.fetch_sessions_to_json(user_id=1)
    print(json_data)