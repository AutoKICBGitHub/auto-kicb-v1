import asyncio
import aiohttp
import time
import json
import os
import re
from datetime import datetime, timedelta
from typing import Dict, List
from faker import Faker

fake_ru = Faker('ru_RU')
fake_en = Faker('en_US')

def load_config():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(script_dir, 'config.json')
    with open(config_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def generate_user_data(index: int, config: Dict) -> Dict:
    unique_id = int(time.time() * 1000000) % 1000000 + index
    
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
    email = f"{first_name_en.lower()}.{last_name_en.lower()}{index}{config['user_generation']['domain_suffix']}"
    crm_ref = f"MTP{unique_id % 100000:05d}"
    
    passport_issue_date = datetime.strptime(config['user_generation']['passport_issue_date'], '%Y-%m-%d')
    passport_expiry_date = passport_issue_date + timedelta(days=config['user_generation']['passport_validity_days'])
    
    return {
        'index': index,
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

def prepare_xml_data(user_data: Dict, config: Dict) -> tuple:
    script_dir = os.path.dirname(os.path.abspath(__file__))
    xml_path = os.path.join(script_dir, config['xml_template_file'])
    
    with open(xml_path, 'r', encoding=config['output']['encoding']) as f:
        xml_data = f.read()
    
    message_id = f"MTP{int(time.time() * 1000000) % 1000000000}-{user_data['index']}"
    
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

async def independent_worker_thread(thread_id: int, session: aiohttp.ClientSession, results: list, config: Dict):
    """Каждый поток работает независимо, делая все свои атаки подряд"""
    endpoint = config['cbs_settings']['endpoint']
    headers = {
        'Content-Type': 'text/xml; charset=utf-8',
        'SOAPAction': config['cbs_settings']['soap_action']
    }
    
    attacks_per_test = config['test_parameters']['attacks_per_test']
    delay_seconds = config['test_parameters']['delay_between_requests']
    timeout = config['cbs_settings']['timeout']
    
    print(f"Поток {thread_id+1} запущен - будет делать {attacks_per_test} атак независимо")
    
    for attack_num in range(attacks_per_test):
        user_index = thread_id * 1000 + attack_num  # Уникальный индекс для каждой атаки
        user_data = generate_user_data(user_index, config)
        xml_data, message_id = prepare_xml_data(user_data, config)
        
        print(f"Поток {thread_id+1}, атака {attack_num+1}/{attacks_per_test}: {user_data['last_name']} {user_data['first_name']}")
        
        request_start = time.time()
        
        try:
            async with session.post(endpoint, data=xml_data, headers=headers, timeout=timeout) as response:
                response_text = await response.text()
                response_time = time.time() - request_start
                
                if "MSGSTAT>SUCCESS" in response_text:
                    customer_match = re.search(r'<CUSTNO>(.*?)</CUSTNO>', response_text)
                    customer_number = customer_match.group(1) if customer_match else None
                    
                    result = {
                        'success': True,
                        'status_code': response.status,
                        'customer_number': customer_number,
                        'message_id': message_id,
                        'response_time': response_time,
                        'user_data': user_data,
                        'error': None,
                        'thread_id': thread_id,
                        'attack_num': attack_num + 1,
                        'full_response': response_text
                    }
                    
                    print(f"  -> УСПЕХ! Клиент #{customer_number} ({response_time:.2f}с)")
                    
                else:
                    error_codes = re.findall(r'<ECODE>(.*?)</ECODE>', response_text)
                    error_descriptions = re.findall(r'<EDESC>(.*?)</EDESC>', response_text)
                    
                    errors = []
                    for code, desc in zip(error_codes, error_descriptions):
                        errors.append(f"{code}: {desc}")
                    
                    result = {
                        'success': False,
                        'status_code': response.status,
                        'customer_number': None,
                        'message_id': message_id,
                        'response_time': response_time,
                        'user_data': user_data,
                        'error': errors if errors else ['Unknown error'],
                        'thread_id': thread_id,
                        'attack_num': attack_num + 1,
                        'full_response': response_text
                    }
                    
                    print(f"  -> ОШИБКА: {errors} ({response_time:.2f}с)")
                    
        except asyncio.TimeoutError:
            result = {
                'success': False,
                'status_code': 0,
                'customer_number': None,
                'message_id': message_id,
                'response_time': timeout,
                'user_data': user_data,
                'error': ['Timeout error'],
                'thread_id': thread_id,
                'attack_num': attack_num + 1,
                'full_response': None
            }
            print(f"  -> ТАЙМАУТ ({timeout}с)")
            
        except Exception as e:
            result = {
                'success': False,
                'status_code': 0,
                'customer_number': None,
                'message_id': message_id,
                'response_time': time.time() - request_start,
                'user_data': user_data,
                'error': [f'Request error: {str(e)}'],
                'thread_id': thread_id,
                'attack_num': attack_num + 1,
                'full_response': None
            }
            print(f"  -> ОШИБКА: {str(e)}")
        
        results.append(result)
        
        # Пауза после каждой атаки (кроме последней)
        if attack_num < attacks_per_test - 1:
            print(f"  -> Поток {thread_id+1} ждет {delay_seconds}с перед следующей атакой...")
            await asyncio.sleep(delay_seconds)
    
    print(f"Поток {thread_id+1} завершил все {attacks_per_test} атак")

async def run_independent_test():
    config = load_config()
    thread_count = config['test_parameters']['thread_count']
    attacks_per_test = config['test_parameters']['attacks_per_test']
    
    print(f"НЕЗАВИСИМЫЙ ТЕСТ CBS")
    print("=" * 50)
    print(f"Потоков: {thread_count}")
    print(f"Атак на поток: {attacks_per_test}")
    print(f"Всего запросов: {thread_count * attacks_per_test}")
    print(f"Пауза между атаками в потоке: {config['test_parameters']['delay_between_requests']}с")
    print(f"Endpoint: {config['cbs_settings']['endpoint']}")
    print("=" * 50)
    print("Каждый поток работает в своем ритме независимо!")
    
    results = []
    start_time = time.time()
    
    async with aiohttp.ClientSession() as session:
        # Запускаем все потоки независимо
        tasks = []
        for thread_id in range(thread_count):
            task = asyncio.create_task(independent_worker_thread(thread_id, session, results, config))
            tasks.append(task)
        
        # Ждем пока все потоки закончат ВСЕ свои атаки
        await asyncio.gather(*tasks)
    
    end_time = time.time()
    total_time = end_time - start_time
    
    # Анализируем результаты
    successful = sum(1 for r in results if r['success'])
    failed = len(results) - successful
    
    successful_users = [r for r in results if r['success']]
    failed_users = [r for r in results if not r['success']]
    
    total_response_time = sum(r['response_time'] for r in successful_users)
    avg_response_time = total_response_time / successful if successful > 0 else 0
    min_response_time = min((r['response_time'] for r in successful_users), default=0)
    max_response_time = max((r['response_time'] for r in successful_users), default=0)
    
    # Статистика по потокам
    thread_stats = {}
    for thread_id in range(thread_count):
        thread_results = [r for r in results if r['thread_id'] == thread_id]
        thread_successful = sum(1 for r in thread_results if r['success'])
        thread_stats[thread_id] = {
            'total': len(thread_results),
            'successful': thread_successful,
            'failed': len(thread_results) - thread_successful,
            'success_rate': thread_successful / len(thread_results) * 100 if thread_results else 0
        }
    
    print(f"\nРЕЗУЛЬТАТЫ НЕЗАВИСИМОГО ТЕСТА:")
    print("=" * 50)
    print(f"Общее время: {total_time:.1f}с")
    print(f"Всего запросов: {len(results)}")
    print(f"Успешных: {successful}")
    print(f"Неуспешных: {failed}")
    print(f"Общий процент успеха: {(successful / len(results) * 100):.1f}%")
    if successful > 0:
        print(f"Среднее время ответа: {avg_response_time:.3f}с")
        print(f"Мин/Макс время: {min_response_time:.3f}с / {max_response_time:.3f}с")
    
    print(f"\nСТАТИСТИКА ПО ПОТОКАМ:")
    for thread_id, stats in thread_stats.items():
        print(f"Поток {thread_id+1}: {stats['successful']}/{stats['total']} успешно ({stats['success_rate']:.1f}%)")
    
    # Сохраняем результаты
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = f"{config['output']['results_prefix']}{timestamp}.json"
    
    final_results = {
        'test_suite': 'CBS Independent Thread Test',
        'timestamp': timestamp,
        'test_type': 'independent_threads',
        'overall_test_time': total_time,
        'configuration': config,
        'thread_statistics': thread_stats,
        'summary': {
            'total_threads': thread_count,
            'attacks_per_thread': attacks_per_test,
            'total_requests': len(results),
            'total_successful': successful,
            'total_failed': failed,
            'overall_success_rate': successful / len(results) * 100 if len(results) > 0 else 0,
            'avg_response_time': avg_response_time,
            'min_response_time': min_response_time,
            'max_response_time': max_response_time,
            'avg_requests_per_second': len(results) / total_time if total_time > 0 else 0
        },
        'all_results': results
    }
    
    with open(log_file, 'w', encoding=config['output']['encoding']) as f:
        json.dump(final_results, f, ensure_ascii=False, indent=2)
    
    print(f"\nФайл: {log_file}")
    
    return final_results

if __name__ == "__main__":
    asyncio.run(run_independent_test()) 