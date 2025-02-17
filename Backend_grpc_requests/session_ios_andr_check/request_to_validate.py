import grpc
import sys
import json
sys.path.append('Backend_grpc_requests')  # Добавляем родительскую директорию в путь для импорта
# Импортируем все из protofile_pb2 чтобы найти правильное имя класса
from protofile_pb2 import *
from protofile_pb2_grpc import WebAuthApiStub

def check_ios_version(ios_version, imei="40C28DFD-3545-43DF-8C90-1671DB97AD5D"):
    # Создаем SSL credentials
    credentials = grpc.ssl_channel_credentials()
    
    # Создаем защищенный канал с правильными настройками SSL
    channel = grpc.secure_channel(
        'newibanktest.kicb.net:443',
        credentials,
        options=(('grpc.ssl_target_name_override', 'newibanktest.kicb.net'),)
    )
    
    # Создаем клиент
    stub = WebAuthApiStub(channel)
    
    # Создаем объект userAgent.ua как в БД
    ua = {
        "osVersion": ios_version,
        "device": "iPhone 12"
    }
    
    # Обновляем метаданные в соответствии с форматом из БД
    metadata = [
        ('ref-id', 'uniqueRefId123123123123'),
        ('device-type', 'ios'),
        # Используем только osVersion из ua
        ('user-agent-c', f'{ua["osVersion"]}; {imei}')
    ]
    
    # Возможно, имя класса в proto-файле другое
    request = LoginRequest(  # Изменено с AuthenticateRequest на LoginRequest
        username="aigerimk",
        password="password1"
    )
    
    try:
        # Отправляем запрос
        response = stub.authenticate(
            request=request,
            metadata=metadata
        )
        success = hasattr(response, 'success') and response.success
        print(f'iOS версия {ios_version}: {"Успешно" if success else "Неуспешно"}')
        return success
    except grpc.RpcError as e:
        print(f'iOS версия {ios_version}: Ошибка - {e}')
        return False
    finally:
        channel.close()

def test_ios_versions():
    # Список актуальных и нестандартных версий iOS
    ios_versions = [
        # Актуальные версии iOS
        "18.3", "18.2.1", "18.2", "18.1.1", "18.1", "18.0.1", "18.0",
        "17.3.1", "17.3", "17.2.1", "17.2", "17.1.2", "17.1.1", "17.1", "17.0.3",
        "17.0.2", "17.0.1", "17.0", "16.7.5", "16.7.4", "16.7.3", "16.7.2", "16.7.1",
        "16.7", "16.6.1", "16.6", "16.5.1", "16.5", "16.4.1", "16.4", "16.3.1",
        "16.3", "16.2", "16.1.2", "16.1.1", "16.1", "16.0.3", "16.0.2", "16.0.1",
        "16.0", "15.7.9", "15.7.8", "15.7.7", "15.7.6", "15.7.5", "15.7.4", "15.7.3",
        
        # Тестирование с ASCII символами в начале
        "@30", "#30", "$30", "&30", "*30", "~30", "`30", "!30", "(30", ")30", "-30", "+30", "=30",
        "{30", "}30", "[30", "]30", ":30", ";30", "'30", "\"30", "<30", ">30", ".30", ",30", "/30",
        "\\30", "|30", "_30", "%30", "^30",
        
        # Тестирование с ASCII символами в конце
        "30@", "30#", "30$", "30&", "30*", "30~", "30`", "30!", "30(", "30)", "30-", "30+", "30=",
        "30{", "30}", "30[", "30]", "30:", "30;", "30'", "30\"", "30<", "30>", "30.", "30,", "30/",
        "30\\", "30|", "30_", "30%", "30^",
        
        # Пробелы и форматирование
        " 33", "33 ",  # Пробелы в начале и конце
        "33.0", "33,1",  # Дробные числа
        
        # Специальные тестовые случаи
        "API33", "Level33", "iOS33",
        "33;", "33)", "33/", "26.1",  # Специальные символы
        "33]", "33}", "33>"  # Разные скобки
    ]
    
    # Создаем словарь для результатов
    results = {
        'working_versions': [],
        'failed_versions': []
    }
    
    # Проверяем версии от 1 до 50 (можно изменить диапазон)
    for ios_version in ios_versions:
        if check_ios_version(ios_version):
            results['working_versions'].append(ios_version)
        else:
            results['failed_versions'].append(ios_version)
    
    # Сохраняем результаты в JSON файл
    with open('ios_version_test_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print("\nИтоговые результаты для iOS:")
    print(f"Работающие версии: {results['working_versions']}")
    print(f"Неработающие версии: {results['failed_versions']}")

if __name__ == '__main__':
    test_ios_versions()
