import grpc
import sys
import json
sys.path.append('Backend_grpc_requests')
from protofile_pb2 import *
from protofile_pb2_grpc import WebAuthApiStub

def check_android_version(android_version, imei="2cdfa88d71801e60"):
    credentials = grpc.ssl_channel_credentials()
    
    channel = grpc.secure_channel(
        'newibanktest.kicb.net:443',
        credentials,
        options=(('grpc.ssl_target_name_override', 'newibanktest.kicb.net'),)
    )
    
    stub = WebAuthApiStub(channel)
    
    # Обновляем метаданные в соответствии с форматом из БД для Android
    metadata = [
        ('ref-id', 'uniqueRefId123123123123'),
        ('device-type', 'android'),
        ('user-agent-c', f'Redmi-Redmi Note 9S,S({android_version}); {imei}')
    ]
    
    request = LoginRequest(
        username="aigerimk",
        password="password1"
    )
    
    try:
        response = stub.authenticate(
            request=request,
            metadata=metadata
        )
        success = hasattr(response, 'success') and response.success
        print(f'Android версия {android_version}: {"Успешно" if success else "Неуспешно"}')
        return success
    except grpc.RpcError as e:
        print(f'Android версия {android_version}: Ошибка - {e}')
        return False
    finally:
        channel.close()

def test_android_versions():
    # Список версий Android для тестирования с API levels
    android_versions = [
        # Последовательное тестирование API levels от -1 до 51
        # *[str(i) for i in range(-1, 52)],
        
        # Некорректные значения
        "abc", "0",
        
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
        "API33", "Level33", "Android33",
        "33;", "33)", "33/", "26.1",  # Специальные символы
        "33]", "33}", "33>"  # Разные скобки
    ]
    
    results = {
        'working_versions': [],
        'failed_versions': []
    }
    
    for android_version in android_versions:
        if check_android_version(android_version):
            results['working_versions'].append(android_version)
        else:
            results['failed_versions'].append(android_version)
    
    with open('android_version_test_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print("\nИтоговые результаты для Android:")
    print(f"Работающие версии: {results['working_versions']}")
    print(f"Неработающие версии: {results['failed_versions']}")

if __name__ == '__main__':
    test_android_versions() 