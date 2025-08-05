import asyncio
import aiohttp
import time
import json
import os
import re
from datetime import datetime, timedelta
from faker import Faker

fake_ru = Faker('ru_RU')
fake_en = Faker('en_US')

def load_config():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(script_dir, 'config.json')
    with open(config_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def generate_user_data(config):
    unique_id = int(time.time() * 1000000) % 1000000
    
    first_name = fake_ru.first_name_male()
    last_name = fake_ru.last_name_male()
    patronymic = fake_ru.middle_name_male()
    
    first_name_en = fake_en.first_name_male()
    last_name_en = fake_en.last_name()
    patronymic_en = fake_en.first_name_male() + 'ovich'
    
    birth_date = datetime.strptime(config['user_generation']['birth_date'], '%Y-%m-%d')
    
    gender_digit = config['user_generation']['gender_code']
    date_str = birth_date.strftime('%d%m%Y')
    random_digits = f"{unique_id % 100000:05d}"
    inn = gender_digit + date_str + random_digits
    
    passport_num = f"ID{8000000 + unique_id}"
    phone = f"99670{unique_id % 10000000:07d}"
    email = f"{first_name_en.lower()}.{last_name_en.lower()}{config['user_generation']['domain_suffix']}"
    crm_ref = f"TEST{unique_id % 100000:05d}"
    
    passport_issue_date = datetime.strptime(config['user_generation']['passport_issue_date'], '%Y-%m-%d')
    passport_expiry_date = passport_issue_date + timedelta(days=config['user_generation']['passport_validity_days'])
    
    return {
        'first_name': first_name,
        'last_name': last_name,
        'patronymic': patronymic,
        'first_name_en': first_name_en,
        'last_name_en': last_name_en,
        'patronymic_en': patronymic_en,
        'inn': inn,
        'passport_num': passport_num,
        'phone': phone,
        'email': email,
        'crm_ref': crm_ref,
        'passport_issue_date': passport_issue_date.strftime("%Y-%m-%d"),
        'passport_expiry_date': passport_expiry_date.strftime("%Y-%m-%d"),
        'unique_id': unique_id
    }

def prepare_xml_data(user_data, config):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    xml_path = os.path.join(script_dir, config['xml_template_file'])
    
    with open(xml_path, 'r', encoding=config['output']['encoding']) as f:
        xml_data = f.read()
    
    message_id = f"TEST{int(time.time() * 1000000) % 1000000000}"
    
    replacements = {
        '{messageId}': message_id,
        '{inn}': user_data['inn'],
        '{first_name}': user_data['first_name'],
        '{last_name}': user_data['last_name'],
        '{patronymic}': user_data['patronymic'],
        '{first_name_en}': user_data['first_name_en'],
        '{last_name_en}': user_data['last_name_en'],
        '{patronymic_en}': user_data['patronymic_en'],
        '{passport_num}': user_data['passport_num'],
        '{phone}': user_data['phone'],
        '{email}': user_data['email'],
        '{crm_ref}': user_data['crm_ref'],
        '{passport_issue_date}': user_data['passport_issue_date'],
        '{passport_expiry_date}': user_data['passport_expiry_date'],
        '{index}': str(user_data['unique_id'])
    }
    
    for old, new in replacements.items():
        xml_data = xml_data.replace(old, new)
    
    return xml_data, message_id

async def test_connection(endpoint):
    """Тестирует базовое TCP соединение"""
    try:
        import socket
        from urllib.parse import urlparse
        
        parsed = urlparse(endpoint)
        host = parsed.hostname
        port = parsed.port
        
        print(f"Проверяем TCP соединение: {host}:{port}")
        
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        result = sock.connect_ex((host, port))
        sock.close()
        
        if result == 0:
            print("✅ TCP соединение успешно")
            return True
        else:
            print(f"❌ TCP соединение неудачно: код {result}")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка проверки соединения: {e}")
        return False

async def test_single_user():
    config = load_config()
    
    print("ТЕСТ ОДНОГО ПОЛЬЗОВАТЕЛЯ CBS")
    print("=" * 50)
    
    # Проверяем соединение
    endpoint = config['cbs_settings']['endpoint']
    tcp_ok = await test_connection(endpoint)
    if not tcp_ok:
        print("Остановка - нет TCP соединения")
        return
    
    # Генерируем пользователя
    user_data = generate_user_data(config)
    xml_data, message_id = prepare_xml_data(user_data, config)
    
    print(f"Пользователь: {user_data['last_name']} {user_data['first_name']}")
    print(f"ИНН: {user_data['inn']}")
    print(f"Паспорт: {user_data['passport_num']}")
    print(f"Телефон: {user_data['phone']}")
    print(f"Email: {user_data['email']}")
    print(f"Message ID: {message_id}")
    print(f"Endpoint: {endpoint}")
    print("-" * 50)
    
    # Отправляем запрос
    headers = {
        'Content-Type': 'text/xml; charset=utf-8',
        'SOAPAction': config['cbs_settings']['soap_action']
    }
    timeout = 60  # Увеличиваем таймаут для диагностики
    
    print("Отправляем SOAP запрос...")
    print(f"Размер XML: {len(xml_data)} байт")
    print(f"Таймаут: {timeout} секунд")
    request_start = time.time()
    
    try:
        connector = aiohttp.TCPConnector(limit=1, limit_per_host=1)
        timeout_settings = aiohttp.ClientTimeout(total=timeout, connect=10, sock_read=30)
        
        async with aiohttp.ClientSession(connector=connector, timeout=timeout_settings) as session:
            print("Устанавливаем HTTP соединение...")
            
            async with session.post(endpoint, data=xml_data, headers=headers) as response:
                print(f"HTTP соединение установлено, статус: {response.status}")
                print("Читаем ответ...")
                
                response_text = await response.text()
                response_time = time.time() - request_start
                
                print(f"Получен ответ: {len(response_text)} байт за {response_time:.3f} секунд")
                print(f"HTTP статус: {response.status}")
                print("-" * 50)
                
                # Анализируем ответ
                if "MSGSTAT>SUCCESS" in response_text:
                    customer_match = re.search(r'<CUSTNO>(.*?)</CUSTNO>', response_text)
                    customer_number = customer_match.group(1) if customer_match else None
                    
                    print("✅ УСПЕХ!")
                    print(f"Номер клиента: {customer_number}")
                    
                    result = {
                        'success': True,
                        'customer_number': customer_number,
                        'response_time': response_time,
                        'status_code': response.status
                    }
                    
                else:
                    # Извлекаем ошибки
                    error_codes = re.findall(r'<ECODE>(.*?)</ECODE>', response_text)
                    error_descriptions = re.findall(r'<EDESC>(.*?)</EDESC>', response_text)
                    
                    errors = []
                    for code, desc in zip(error_codes, error_descriptions):
                        errors.append(f"{code}: {desc}")
                    
                    print("❌ ОШИБКА!")
                    for error in errors:
                        print(f"  {error}")
                    
                    # Показываем первые 500 символов ответа для анализа
                    print(f"\nПервые 500 символов ответа:")
                    print(response_text[:500])
                    
                    result = {
                        'success': False,
                        'customer_number': None,
                        'response_time': response_time,
                        'status_code': response.status,
                        'errors': errors
                    }
                
                # Сохраняем результат
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                result_file = f"single_user_test_{timestamp}.json"
                
                full_result = {
                    'test_type': 'Single User Test',
                    'timestamp': timestamp,
                    'user_data': user_data,
                    'message_id': message_id,
                    'result': result,
                    'full_response': response_text,
                    'request_xml': xml_data
                }
                
                with open(result_file, 'w', encoding='utf-8') as f:
                    json.dump(full_result, f, ensure_ascii=False, indent=2)
                
                print(f"\nПолный результат сохранен в: {result_file}")
                
                return result
                
    except asyncio.TimeoutError:
        elapsed = time.time() - request_start
        print(f"❌ ТАЙМАУТ! ({elapsed:.1f} секунд)")
        print("Возможные причины:")
        print("- CBS сервер не отвечает на SOAP запросы")
        print("- Слишком медленная обработка")
        print("- Проблемы с XML форматом")
        return {'success': False, 'error': 'Timeout'}
        
    except aiohttp.ClientConnectorError as e:
        print(f"❌ ОШИБКА СОЕДИНЕНИЯ: {str(e)}")
        print("Возможные причины:")
        print("- CBS сервер не запущен")
        print("- Неправильный адрес/порт")
        print("- Проблемы с SSH туннелем")
        return {'success': False, 'error': str(e)}
        
    except Exception as e:
        print(f"❌ ДРУГАЯ ОШИБКА: {str(e)}")
        print(f"Тип ошибки: {type(e).__name__}")
        return {'success': False, 'error': str(e)}

if __name__ == "__main__":
    asyncio.run(test_single_user()) 