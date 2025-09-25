import paramiko
import time
from datetime import datetime
import os

class ServiceMonitor:
    def __init__(self, 
                 host="newibanktest.kicb.net",
                 username="your_username",
                 password="your_password",
                 log_path="/var/log/ibank/service.log",  # путь к логам на сервере
                 local_log_dir="service_logs"):
        self.host = host
        self.username = username
        self.password = password
        self.log_path = log_path
        self.local_log_dir = os.path.join("C:/project_kicb/side_proj/astrasend_tests", local_log_dir)
        
        if not os.path.exists(self.local_log_dir):
            os.makedirs(self.local_log_dir)

    def start_monitoring(self, operation_id=None, lines=300):
        """
        Мониторит логи сервиса
        
        Args:
            operation_id: Если указан, фильтрует логи только для этой операции
            lines: Количество последних строк для отслеживания
        """
        try:
            # Подключаемся к серверу
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(self.host, username=self.username, password=self.password)
            
            # Команда для получения последних строк лога
            tail_cmd = f"tail -n {lines} -f {self.log_path}"
            if operation_id:
                tail_cmd = f"{tail_cmd} | grep {operation_id}"
            
            # Запускаем команду
            stdin, stdout, stderr = ssh.exec_command(tail_cmd)
            
            # Имя файла для локального лога
            local_log_file = os.path.join(
                self.local_log_dir,
                f"service_monitor_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
            )
            
            print(f"Начинаем мониторинг сервиса...")
            print(f"Логи сохраняются в: {local_log_file}")
            print("Нажмите Ctrl+C для остановки")
            
            # Читаем и сохраняем логи
            with open(local_log_file, 'w', encoding='utf-8') as f:
                while True:
                    line = stdout.readline()
                    if not line:
                        break
                        
                    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    formatted_line = f"[{timestamp}] {line.strip()}"
                    
                    print(formatted_line)
                    f.write(formatted_line + '\n')
                    f.flush()  # Сразу записываем на диск
                    
        except KeyboardInterrupt:
            print("\nМониторинг остановлен пользователем")
        except Exception as e:
            print(f"Ошибка при мониторинге: {str(e)}")
        finally:
            if 'ssh' in locals():
                ssh.close()

def monitor_with_operation(operation_id):
    """Запускает мониторинг для конкретной операции"""
    monitor = ServiceMonitor()
    monitor.start_monitoring(operation_id=operation_id)

def monitor_service():
    """Запускает общий мониторинг сервиса"""
    monitor = ServiceMonitor()
    monitor.start_monitoring()

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Мониторинг логов сервиса')
    parser.add_argument('--operation-id', help='ID операции для фильтрации логов')
    parser.add_argument('--lines', type=int, default=300, help='Количество последних строк для отслеживания')
    
    args = parser.parse_args()
    
    monitor = ServiceMonitor()
    monitor.start_monitoring(operation_id=args.operation_id, lines=args.lines)
