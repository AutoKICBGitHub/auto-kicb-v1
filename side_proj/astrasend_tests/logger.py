import json
from datetime import datetime
import os

class TransferLogger:
    def __init__(self, log_dir=None):
        if log_dir is None:
            # Используем абсолютный путь к директории проекта
            project_dir = "C:/project_kicb/side_proj/astrasend_tests"
            self.log_dir = os.path.join(project_dir, "logs")
        else:
            self.log_dir = log_dir
        self._ensure_log_directory()
        print(f"Логи сохраняются в: {self.log_dir}")
        
    def _ensure_log_directory(self):
        """Создает директорию для логов, если она не существует"""
        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir)
            
    def _get_log_filename(self):
        """Генерирует имя файла лога на основе текущей даты"""
        current_date = datetime.now().strftime("%Y%m%d")
        return f"{current_date}_astrosend_logs.json"
        
    def _get_readable_log_filename(self):
        """Генерирует имя файла для читабельного лога"""
        return "astrosend.log"

    def log_transfer(self, operation_id: str, request_data: dict, response_data: dict, status: str):
        """
        Записывает информацию о трансфере в лог файлы
        
        Args:
            operation_id: ID операции
            request_data: Данные запроса
            response_data: Данные ответа
            status: Статус операции (create/confirm/error)
        """
        # Создаем запись для JSON лога
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "operation_id": operation_id,
            "status": status,
            "request": request_data,
            "response": response_data
        }
        
        # Путь к JSON логу
        json_log_file = os.path.join(self.log_dir, self._get_log_filename())
        
        # Читаем существующие JSON логи или создаем новый список
        if os.path.exists(json_log_file):
            with open(json_log_file, 'r', encoding='utf-8') as f:
                try:
                    logs = json.load(f)
                except json.JSONDecodeError:
                    logs = []
        else:
            logs = []
        
        # Добавляем новую запись в JSON лог
        logs.append(log_entry)
        
        # Сохраняем обновленные JSON логи
        with open(json_log_file, 'w', encoding='utf-8') as f:
            json.dump(logs, f, ensure_ascii=False, indent=4)
            
        # Создаем читабельную версию лога
        readable_log_file = os.path.join(self.log_dir, self._get_readable_log_filename())
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        with open(readable_log_file, 'a', encoding='utf-8') as f:
            # Заголовок операции
            f.write(f"[{timestamp}] {'='*50} НОВАЯ ОПЕРАЦИЯ {'='*50}\n")
            f.write(f"[{timestamp}] Operation ID: {operation_id}\n")
            f.write(f"[{timestamp}] Статус: {status}\n")
            
            # Данные запроса
            f.write(f"[{timestamp}] ЗАПРОС:\n")
            for line in json.dumps(request_data, indent=2, ensure_ascii=False).split('\n'):
                f.write(f"[{timestamp}] {line}\n")
            
            # Данные ответа
            f.write(f"[{timestamp}] ОТВЕТ:\n")
            for line in json.dumps(response_data, indent=2, ensure_ascii=False).split('\n'):
                f.write(f"[{timestamp}] {line}\n")
            
            f.write(f"[{timestamp}] {'='*120}\n\n")
            
    def get_transfer_logs(self, operation_id: str = None, date: str = None):
        """
        Получает логи по ID операции или дате
        
        Args:
            operation_id: ID операции для фильтрации
            date: Дата в формате YYYYMMDD для фильтрации
        """
        if date is None:
            date = datetime.now().strftime("%Y%m%d")
            
        log_file = os.path.join(self.log_dir, f"{date}_astrosend_logs.json")
        
        if not os.path.exists(log_file):
            return []
            
        with open(log_file, 'r', encoding='utf-8') as f:
            try:
                logs = json.load(f)
                if operation_id:
                    logs = [log for log in logs if log["operation_id"] == operation_id]
                return logs
            except json.JSONDecodeError:
                return []
