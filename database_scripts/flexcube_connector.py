import paramiko
import subprocess
import time


def setup_ssh_connection(hostname, username, private_key_path, local_port, remote_host, remote_port):
    """
    Настройка SSH-подключения с использованием paramiko.
    :param hostname: адрес SSH-сервера
    :param username: имя пользователя
    :param private_key_path: путь к приватному ключу
    :param local_port: локальный порт для перенаправления
    :param remote_host: удаленный хост для перенаправления
    :param remote_port: удаленный порт для перенаправления
    """
    try:
        print(f"Подключение к серверу {hostname} с пользователем {username}...")
        ssh_client = paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh_client.connect(hostname=hostname, username=username, key_filename=private_key_path)

        # Настройка туннеля
        print(f"Настройка туннеля: localhost:{local_port} -> {remote_host}:{remote_port}")
        transport = ssh_client.get_transport()
        transport.request_port_forward('localhost', local_port, remote_host, remote_port)

        print(f"Туннель открыт: localhost:{local_port} -> {remote_host}:{remote_port}")
        return ssh_client
    except Exception as e:
        print(f"Ошибка подключения к серверу {hostname}: {e}")
        raise


def setup_local_tunnel(local_port, remote_host, remote_port):
    """
    Настройка локального туннеля без использования SSH (внешний процесс ssh).
    :param local_port: локальный порт
    :param remote_host: удаленный хост
    :param remote_port: удаленный порт
    """
    try:
        command = [
            "ssh",
            "-o", "ServerAliveInterval=60",
            "-L", f"{local_port}:{remote_host}:{remote_port}",
            "ibank_user@192.168.190.46"
        ]
        print(f"Запуск команды: {' '.join(command)}")
        process = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print(f"Локальный туннель запущен: localhost:{local_port} -> {remote_host}:{remote_port}")
        return process
    except Exception as e:
        print(f"Ошибка настройки локального туннеля: {e}")
        raise


if __name__ == "__main__":
    try:
        # Параметры первого SSH-сервера
        first_server = {
            "ssh_address": "172.30.201.71",
            "ssh_username": "ibank_dev",
            "private_key_path": "C:\\Users\\User\\.ssh\\id_rsa",
            "local_port": 8101,
            "remote_host": "localhost",
            "remote_port": 8101,
        }

        # Параметры второго соединения
        second_tunnel = {
            "local_port": 8101,
            "remote_host": "192.168.190.101",
            "remote_port": 8101,
        }

        # Подключение к первому серверу через SSH
        ssh_client_1 = setup_ssh_connection(
            hostname=first_server["ssh_address"],
            username=first_server["ssh_username"],
            private_key_path=first_server["private_key_path"],
            local_port=first_server["local_port"],
            remote_host=first_server["remote_host"],
            remote_port=first_server["remote_port"],
        )

        # Настройка второго туннеля без SSH
        second_tunnel_process = setup_local_tunnel(
            local_port=second_tunnel["local_port"],
            remote_host=second_tunnel["remote_host"],
            remote_port=second_tunnel["remote_port"],
        )

        print("Все подключения успешно настроены!")
        print("Теперь вы можете получить доступ по адресу: https://localhost:8101/FCJNeoWeb/SMMDIFRM.jsp")

        # Оставляем соединения активными
        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        print("\nЗакрытие соединений...")
    finally:
        if 'second_tunnel_process' in locals():
            second_tunnel_process.terminate()
            print("Локальный туннель закрыт.")
        if 'ssh_client_1' in locals():
            ssh_client_1.close()
            print("Подключение к первому серверу закрыто.")
