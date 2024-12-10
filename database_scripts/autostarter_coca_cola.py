from sshtunnel import SSHTunnelForwarder
import paramiko

# Параметры первого SSH-сервера
first_server = {
    "ssh_address": "172.30.201.71",
    "ssh_username": "ibank_dev",
    "private_key_path": "C:\\Users\\User\\.ssh\\id_rsa",  # Путь к приватному ключу
    "local_bind_ports": [(30523, 33331), (5434, 55559)]  # Локальные порты : Удаленные порты
}

# Параметры второго SSH-сервера (через первый сервер)
second_server = {
    "ssh_address": "192.168.190.46",
    "ssh_username": "ibank_user",
    "local_bind_ports": [(55559, 5432)]  # Локальные порты : Удаленные порты
}


def setup_ssh_tunnel(server_details, ssh_client=None):
    """
    Настройка SSH-туннеля с помощью sshtunnel.
    :param server_details: параметры сервера
    :param ssh_client: объект SSH-клиента для туннелирования через первый сервер (если требуется)
    """
    tunnels = []
    try:
        for local_port, remote_port in server_details["local_bind_ports"]:
            print(f"Настройка туннеля: localhost:{local_port} -> {server_details['ssh_address']}:{remote_port}")

            if ssh_client:
                # Используем paramiko напрямую для туннеля через уже установленное подключение
                transport = ssh_client.get_transport()
                channel = transport.open_channel(
                    "direct-tcpip",
                    dest_addr=("localhost", remote_port),
                    src_addr=("0.0.0.0", local_port)
                )
                tunnels.append(channel)
                print(f"Туннель открыт: localhost:{local_port} -> {server_details['ssh_address']}:{remote_port}")
            else:
                # Обычное подключение через sshtunnel
                tunnel = SSHTunnelForwarder(
                    (server_details["ssh_address"], 22),
                    ssh_username=server_details["ssh_username"],
                    ssh_pkey=server_details["private_key_path"],
                    local_bind_address=('0.0.0.0', local_port),
                    remote_bind_address=('localhost', remote_port),
                )
                tunnel.start()
                tunnels.append(tunnel)
                print(f"Туннель открыт: localhost:{local_port} -> {server_details['ssh_address']}:{remote_port}")

        return tunnels

    except Exception as e:
        print(f"Ошибка настройки туннеля: {e}")
        return None


def close_tunnels(tunnels):
    """
    Закрытие всех туннелей.
    """
    for tunnel in tunnels:
        if isinstance(tunnel, SSHTunnelForwarder):
            tunnel.stop()
            print(f"Туннель {tunnel.local_bind_port} закрыт.")
        else:
            # Закрытие каналов paramiko
            tunnel.close()
            print("Канал paramiko закрыт.")


if __name__ == "__main__":
    try:
        # Подключение к первому серверу
        print("Подключение к первому серверу...")
        ssh_client = paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh_client.connect(
            hostname=first_server["ssh_address"],
            username=first_server["ssh_username"],
            key_filename=first_server["private_key_path"]
        )
        print("Подключение к первому серверу установлено.")

        # Настройка туннелей для первого сервера
        first_tunnels = setup_ssh_tunnel(first_server)
        if not first_tunnels:
            print("Не удалось настроить туннели на первом сервере.")
            exit()

        print("Первый сервер настроен. Теперь подключаемся ко второму серверу...")

        # Настройка туннелей для второго сервера через paramiko
        second_tunnels = setup_ssh_tunnel(second_server, ssh_client=ssh_client)
        if not second_tunnels:
            print("Не удалось настроить туннели на втором сервере.")
            close_tunnels(first_tunnels)
            exit()

        print("Все туннели успешно настроены!")

        # Оставляем туннели активными
        print("Туннели активны. Нажмите Ctrl+C для завершения.")
        while True:
            pass

    except KeyboardInterrupt:
        print("Закрытие туннелей...")

    finally:
        if 'second_tunnels' in locals():
            close_tunnels(second_tunnels)
        if 'first_tunnels' in locals():
            close_tunnels(first_tunnels)
        if 'ssh_client' in locals():
            ssh_client.close()
            print("Подключение к первому серверу закрыто.")
