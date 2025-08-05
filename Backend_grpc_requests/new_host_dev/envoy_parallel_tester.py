#!/usr/bin/env python3
import grpc
import json
import uuid
import sys
import os
import time
import threading
import requests
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
import pandas as pd

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from protofile_pb2_grpc import WebAccountApiStub, WebAccountV2ApiStub, WebDirectoryApiStub
from protofile_pb2 import WebAccountsRequest, IncomingWebDirectory

class EnvoyLoadTester:
    def __init__(self):
        self.server = 'newibankdevcorp.kicb.net:443'
        self.options = [('grpc.max_receive_message_length', -1), ('grpc.max_send_message_length', -1)]
        self.session_data = {
            'sessionKey': '1jhqCaBADD96rOX8dwRi8Y',
            'sessionId': '6vWtxJzAxt7MJoxyDFVjZ5',
            'device-type': 'ios',
            'x-real-ip': '93.170.8.20',
            'user-agent': '{"ua": {"device": "iPhone X", "osVersion": "16.7.7"}, "imei": "A428AB95-421E-4D78-9A86-0D6BDB1E39C6", "deviceName": "", "deviceType": "ios", "macAddress": "A428AB95-421E-4D78-9A86-0D6BDB1E39C6"}',
            'user-agent-c': '16.7.7; iPhone X',
            'app-type': 'I',
            'imei': 'A428AB95-421E-4D78-9A86-0D6BDB1E39C6',
            'userId': '134'
        }
        self.results = []
        self.thread_stats = {}  # Статистика по потокам
        self.errors = []  # Список всех ошибок
        self.lock = threading.Lock()

    def get_session_metadata(self):
        return [
            ('sessionkey', self.session_data['sessionKey']),
            ('sessionid', self.session_data['sessionId']),
            ('device-type', self.session_data['device-type']),
            ('refid', str(uuid.uuid4())),
            ('x-real-ip', self.session_data['x-real-ip']),
            ('user-agent', self.session_data['user-agent']),
            ('user-agent-c', self.session_data['user-agent-c']),
            ('app-type', self.session_data['app-type']),
            ('imei', self.session_data['imei'])
            # Убрал userid из метаданных - передается только в data
        ]

    def get_basic_metadata(self):
        return [('refid', str(uuid.uuid4())), ('device-type', 'ios')]
    
    def measure_internet_speed(self):
        """Измеряет скорость интернета простым HTTP запросом"""
        try:
            start_time = time.time()
            response = requests.get('https://httpbin.org/get', timeout=5)
            end_time = time.time()
            if response.status_code == 200:
                # Примерный расчет скорости (размер ответа / время)
                response_size = len(response.content)
                response_time = end_time - start_time
                speed_kbps = (response_size / 1024) / response_time
                return round(speed_kbps, 2)
            return 0
        except:
            return 0
    
    def init_thread_stats(self, thread_id):
        """Инициализирует статистику для потока"""
        with self.lock:
            self.thread_stats[thread_id] = {
                'thread_id': thread_id,
                'start_time': datetime.now(),
                'end_time': None,
                'internet_speed_start': self.measure_internet_speed(),
                'internet_speed_end': 0,
                'total_requests': 0,
                'successful_requests': 0,
                'failed_requests': 0,
                'response_times': [],
                'apis_tested': {
                    'WebAccountApi': {'requests': 0, 'success': 0, 'avg_time': 0},
                    'WebAccountV2Api': {'requests': 0, 'success': 0, 'avg_time': 0},
                    'WebDirectoryApi': {'requests': 0, 'success': 0, 'avg_time': 0}
                }
            }
    
    def update_thread_stats(self, thread_id, api_name, response_time_ms, success):
        """Обновляет статистику потока"""
        with self.lock:
            if thread_id in self.thread_stats:
                stats = self.thread_stats[thread_id]
                stats['total_requests'] += 1
                stats['response_times'].append(response_time_ms)
                
                if success:
                    stats['successful_requests'] += 1
                else:
                    stats['failed_requests'] += 1
                
                # Обновляем статистику по API
                if api_name in stats['apis_tested']:
                    api_stats = stats['apis_tested'][api_name]
                    api_stats['requests'] += 1
                    if success:
                        api_stats['success'] += 1
                    
                    # Пересчитываем среднее время
                    if api_stats['requests'] > 0:
                        current_times = [t for t in stats['response_times']]
                        api_times = current_times[-api_stats['requests']:]
                        api_stats['avg_time'] = round(sum(api_times) / len(api_times), 2)

    def record_result(self, thread_id, attack_num, api_name, endpoint, start_time, end_time, success, error_code=None, response_size=0):
        """Записывает результат запроса в общий список и обновляет статистику потока"""
        response_time_ms = round((end_time - start_time) * 1000, 2)
        
        with self.lock:
            self.results.append({
                'timestamp': datetime.fromtimestamp(start_time).strftime('%Y-%m-%d %H:%M:%S.%f')[:-3],
                'thread_id': thread_id,
                'attack_number': attack_num,
                'api_name': api_name,
                'endpoint': endpoint,
                'response_time_ms': response_time_ms,
                'success': success,
                'error_code': error_code,
                'response_size_bytes': response_size
            })
        
        # Обновляем статистику потока
        self.update_thread_stats(thread_id, api_name, response_time_ms, success)
    
    def log_error(self, thread_id, api_name, endpoint, error_message, attack_num=None):
        """Записывает ошибку в список и выводит в консоль"""
        error_info = {
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3],
            'thread_id': thread_id,
            'attack_number': attack_num,
            'api_name': api_name,
            'endpoint': endpoint,
            'error_message': str(error_message)
        }
        
        with self.lock:
            self.errors.append(error_info)
            # Выводим ошибку в консоль сразу
            print(f"❌ [Поток {thread_id}] {api_name}.{endpoint}: {error_message}")
        
        return str(error_message)
    
    def finalize_thread_stats(self, thread_id):
        """Завершает сбор статистики для потока"""
        with self.lock:
            if thread_id in self.thread_stats:
                stats = self.thread_stats[thread_id]
                stats['end_time'] = datetime.now()
                stats['internet_speed_end'] = self.measure_internet_speed()
                
                # Рассчитываем общие метрики
                if stats['response_times']:
                    stats['avg_response_time'] = round(sum(stats['response_times']) / len(stats['response_times']), 2)
                    stats['min_response_time'] = round(min(stats['response_times']), 2)
                    stats['max_response_time'] = round(max(stats['response_times']), 2)
                else:
                    stats['avg_response_time'] = 0
                    stats['min_response_time'] = 0
                    stats['max_response_time'] = 0
                
                stats['success_rate'] = round((stats['successful_requests'] / stats['total_requests']) * 100, 2) if stats['total_requests'] > 0 else 0
                stats['duration_seconds'] = (stats['end_time'] - stats['start_time']).total_seconds()
    
    def get_v2_metadata(self):
        """Метаданные для WebAccountV2Api и WebTransferApi - без sessionid (передается в data)"""
        return [
            ('sessionkey', self.session_data['sessionKey']),
            # sessionid убираем - передается в data
            ('device-type', self.session_data['device-type']),
            ('refid', str(uuid.uuid4())),
            ('x-real-ip', self.session_data['x-real-ip']),
            ('user-agent', self.session_data['user-agent']),
            ('user-agent-c', self.session_data['user-agent-c']),
            ('app-type', self.session_data['app-type']),
            ('imei', self.session_data['imei'])
        ]

    def test_webaccount_api(self, thread_id, attack_num):
        channel = grpc.secure_channel(self.server, grpc.ssl_channel_credentials(), self.options)
        stub = WebAccountApiStub(channel)
        for endpoint in ['GET_ACCOUNTS', 'GET_LOANS', 'GET_DEPOSITS']:
            start_time = time.time()
            try:
                data = {"userId": int(self.session_data['userId'])}
                request = WebAccountsRequest(code=endpoint, data=json.dumps(data))
                metadata = self.get_session_metadata()
                response = stub.makeWebAccount(request, metadata=metadata)
                end_time = time.time()
                
                if response.success:
                    response_size = len(response.data) if hasattr(response, 'data') and response.data else 0
                    self.record_result(thread_id, attack_num, 'WebAccountApi', endpoint, start_time, end_time, True, response_size=response_size)
                else:
                    error_code = response.error.code if response.error else "UNKNOWN_ERROR"
                    error_msg = response.error.message if response.error and hasattr(response.error, 'message') else "Неизвестная ошибка сервера"
                    full_error = f"{error_code}: {error_msg}"
                    logged_error = self.log_error(thread_id, 'WebAccountApi', endpoint, full_error, attack_num)
                    self.record_result(thread_id, attack_num, 'WebAccountApi', endpoint, start_time, end_time, False, logged_error)
            except Exception as e:
                end_time = time.time()
                logged_error = self.log_error(thread_id, 'WebAccountApi', endpoint, f"Exception: {str(e)}", attack_num)
                self.record_result(thread_id, attack_num, 'WebAccountApi', endpoint, start_time, end_time, False, logged_error)
        channel.close()

    def test_webaccount_v2_api(self, thread_id, attack_num):
        channel = grpc.secure_channel(self.server, grpc.ssl_channel_credentials(), self.options)
        stub = WebAccountV2ApiStub(channel)
        endpoints = [
            ('GET_LIST_OF_STORIES', {}),
            ('GET_ACCOUNTS', {'accountStatus': 'O'}),
            ('GET_EXCHANGE_RATE', {'rateType': 'cash'}),
            ('GET_LIST_OF_TEMPLATES', {'pageNumber': 1, 'pageSize': 20, 'templateName': ''})
        ]
        for endpoint, data in endpoints:
            start_time = time.time()
            try:
                data['userId'] = int(self.session_data['userId'])
                data['sessionId'] = self.session_data['sessionId']
                request = WebAccountsRequest(code=endpoint, data=json.dumps(data))
                metadata = self.get_v2_metadata()
                response = stub.makeWebAccountV2(request, metadata=metadata)
                end_time = time.time()
                
                if response.success:
                    response_size = len(response.data) if hasattr(response, 'data') and response.data else 0
                    self.record_result(thread_id, attack_num, 'WebAccountV2Api', endpoint, start_time, end_time, True, response_size=response_size)
                else:
                    error_code = response.error.code if response.error else "UNKNOWN_ERROR"
                    error_msg = response.error.message if response.error and hasattr(response.error, 'message') else "Неизвестная ошибка сервера"
                    full_error = f"{error_code}: {error_msg}"
                    logged_error = self.log_error(thread_id, 'WebAccountV2Api', endpoint, full_error, attack_num)
                    self.record_result(thread_id, attack_num, 'WebAccountV2Api', endpoint, start_time, end_time, False, logged_error)
            except Exception as e:
                end_time = time.time()
                logged_error = self.log_error(thread_id, 'WebAccountV2Api', endpoint, f"Exception: {str(e)}", attack_num)
                self.record_result(thread_id, attack_num, 'WebAccountV2Api', endpoint, start_time, end_time, False, logged_error)
        channel.close()

    def test_webdirectory_api(self, thread_id, attack_num):
        channel = grpc.secure_channel(self.server, grpc.ssl_channel_credentials(), self.options)
        stub = WebDirectoryApiStub(channel)
        for endpoint in ['GET_DIRECTORY_EXCHANGE_RATES', 'GET_DV_OF_DIRECTORIES', 'GET_DIRECTORY_BRANCHES_ATMS']:
            start_time = time.time()
            try:
                request = IncomingWebDirectory(code=endpoint, data=None)
                metadata = self.get_basic_metadata()
                response = stub.makeWebDirectory(request, metadata=metadata)
                end_time = time.time()
                
                if response.data and len(response.data) > 0:
                    response_size = len(response.data)
                    self.record_result(thread_id, attack_num, 'WebDirectoryApi', endpoint, start_time, end_time, True, response_size=response_size)
                else:
                    logged_error = self.log_error(thread_id, 'WebDirectoryApi', endpoint, "EMPTY_RESPONSE: Сервер вернул пустой ответ", attack_num)
                    self.record_result(thread_id, attack_num, 'WebDirectoryApi', endpoint, start_time, end_time, False, logged_error)
            except Exception as e:
                end_time = time.time()
                logged_error = self.log_error(thread_id, 'WebDirectoryApi', endpoint, f"Exception: {str(e)}", attack_num)  
                self.record_result(thread_id, attack_num, 'WebDirectoryApi', endpoint, start_time, end_time, False, logged_error)
        channel.close()


    def worker_thread(self, thread_id):
        """Выполняет 10 атак в одном потоке"""
        # Инициализируем статистику потока
        self.init_thread_stats(thread_id)
        
        for attack_num in range(1, 11):
            # Каждая атака тестирует все 3 API
            self.test_webaccount_api(thread_id, attack_num)
            self.test_webaccount_v2_api(thread_id, attack_num)
            self.test_webdirectory_api(thread_id, attack_num)
        
        # Финализируем статистику потока
        self.finalize_thread_stats(thread_id)
    
    def save_to_excel(self):
        """Сохраняет статистику по потокам в Excel файл"""
        if not self.thread_stats:
            print("Нет данных для сохранения")
            return
        
        # Сохраняем в той же папке где находится скрипт
        script_dir = os.path.dirname(os.path.abspath(__file__))
        filename = os.path.join(script_dir, f"thread_stats_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx")
        
        with pd.ExcelWriter(filename, engine='openpyxl') as writer:
            # ОСНОВНАЯ СТАТИСТИКА ПО ПОТОКАМ
            thread_data = []
            for thread_id, stats in self.thread_stats.items():
                thread_data.append({
                    'Поток №': thread_id,
                    'Время старта': stats['start_time'].strftime('%H:%M:%S'),
                    'Время завершения': stats['end_time'].strftime('%H:%M:%S'),
                    'Длительность (сек)': stats['duration_seconds'],
                    'Всего запросов': stats['total_requests'],
                    'Успешных запросов': stats['successful_requests'],
                    'Неудачных запросов': stats['failed_requests'],
                    'Процент успеха (%)': stats['success_rate'],
                    'Среднее время ответа (мс)': stats['avg_response_time'],
                    'Минимальное время ответа (мс)': stats['min_response_time'],
                    'Максимальное время ответа (мс)': stats['max_response_time'],
                    'Скорость интернета в начале (КБ/с)': stats['internet_speed_start'],
                    'Скорость интернета в конце (КБ/с)': stats['internet_speed_end']
                })
            
            thread_df = pd.DataFrame(thread_data)
            thread_df.to_excel(writer, sheet_name='Статистика по потокам', index=False)
            
            # ДЕТАЛИЗАЦИЯ ПО API ДЛЯ КАЖДОГО ПОТОКА
            api_details = []
            for thread_id, stats in self.thread_stats.items():
                for api_name, api_stats in stats['apis_tested'].items():
                    if api_stats['requests'] > 0:  # Только если были запросы
                        success_rate = round((api_stats['success'] / api_stats['requests']) * 100, 2) if api_stats['requests'] > 0 else 0
                        api_details.append({
                            'Поток №': thread_id,
                            'API': api_name,
                            'Всего запросов': api_stats['requests'],
                            'Успешных': api_stats['success'],
                            'Процент успеха (%)': success_rate,
                            'Среднее время ответа (мс)': api_stats['avg_time']
                        })
            
            api_df = pd.DataFrame(api_details)
            api_df.to_excel(writer, sheet_name='Детализация по API', index=False)
            
            # ОБЩАЯ СВОДКА
            total_requests = sum(stats['total_requests'] for stats in self.thread_stats.values())
            total_successful = sum(stats['successful_requests'] for stats in self.thread_stats.values())
            avg_internet_speed_start = round(sum(stats['internet_speed_start'] for stats in self.thread_stats.values()) / len(self.thread_stats), 2)
            avg_internet_speed_end = round(sum(stats['internet_speed_end'] for stats in self.thread_stats.values()) / len(self.thread_stats), 2)
            
            all_response_times = []
            for stats in self.thread_stats.values():
                all_response_times.extend(stats['response_times'])
            
            summary_data = [{
                'Параметр': 'Общее количество потоков',
                'Значение': len(self.thread_stats)
            }, {
                'Параметр': 'Всего запросов',
                'Значение': total_requests
            }, {
                'Параметр': 'Успешных запросов',
                'Значение': total_successful
            }, {
                'Параметр': 'Общий процент успеха (%)',
                'Значение': round((total_successful / total_requests) * 100, 2) if total_requests > 0 else 0
            }, {
                'Параметр': 'Среднее время ответа (мс)',
                'Значение': round(sum(all_response_times) / len(all_response_times), 2) if all_response_times else 0
            }, {
                'Параметр': 'Минимальное время ответа (мс)',
                'Значение': round(min(all_response_times), 2) if all_response_times else 0
            }, {
                'Параметр': 'Максимальное время ответа (мс)',
                'Значение': round(max(all_response_times), 2) if all_response_times else 0
            }, {
                'Параметр': 'Средняя скорость интернета в начале (КБ/с)',
                'Значение': avg_internet_speed_start
            }, {
                'Параметр': 'Средняя скорость интернета в конце (КБ/с)',
                'Значение': avg_internet_speed_end
            }]
            
            summary_df = pd.DataFrame(summary_data)
            summary_df.to_excel(writer, sheet_name='Общая сводка', index=False)
            
            # ЛИСТ С ОШИБКАМИ
            if self.errors:
                errors_df = pd.DataFrame(self.errors)
                errors_df.to_excel(writer, sheet_name='Ошибки', index=False)
                
                # СТАТИСТИКА ОШИБОК
                error_stats = []
                error_counts = {}
                for error in self.errors:
                    api_endpoint = f"{error['api_name']}.{error['endpoint']}"
                    if api_endpoint not in error_counts:
                        error_counts[api_endpoint] = 0
                    error_counts[api_endpoint] += 1
                
                for api_endpoint, count in sorted(error_counts.items(), key=lambda x: x[1], reverse=True):
                    error_stats.append({
                        'API.Endpoint': api_endpoint,
                        'Количество ошибок': count
                    })
                
                if error_stats:
                    error_stats_df = pd.DataFrame(error_stats)
                    error_stats_df.to_excel(writer, sheet_name='Статистика ошибок', index=False)
            
        print(f"✅ Статистика по потокам сохранена в файл: {os.path.basename(filename)}")
        print(f"📁 Полный путь: {filename}")
        
        # Краткая статистика в консоль
        print(f"\n📊 РЕЗУЛЬТАТЫ НАГРУЗОЧНОГО ТЕСТА:")
        print(f"   🧵 Потоков: {len(self.thread_stats)}")
        print(f"   📝 Всего запросов: {total_requests}")
        print(f"   ✅ Успешных: {total_successful} ({round((total_successful/total_requests)*100, 1)}%)")
        print(f"   ❌ Ошибок: {len(self.errors)}")
        print(f"   ⏱️  Среднее время ответа: {round(sum(all_response_times)/len(all_response_times), 2)} мс")
        print(f"   🌐 Скорость интернета: {avg_internet_speed_start} → {avg_internet_speed_end} КБ/с")
        
        # Показываем топ ошибок
        if self.errors:
            print(f"\n🚨 ТОП ОШИБОК:")
            error_counts = {}
            for error in self.errors:
                error_key = error['error_message']
                if error_key not in error_counts:
                    error_counts[error_key] = 0
                error_counts[error_key] += 1
            
            for error_msg, count in sorted(error_counts.items(), key=lambda x: x[1], reverse=True)[:5]:
                print(f"   • {error_msg} ({count}x)")
        
        print(f"\n🧵 РЕЗУЛЬТАТЫ ПО ПОТОКАМ:")
        for thread_id, stats in sorted(self.thread_stats.items()):
            print(f"   Поток #{thread_id}: {stats['success_rate']}% успех, {stats['avg_response_time']}мс среднее время")

    def run_load_test(self):
        print("🚀 ЗАПУСК НАГРУЗОЧНОГО ТЕСТА ENVOY")
        print("=" * 50)
        print(f"📊 Параметры теста:")
        print(f"   🧵 Потоков: 5")
        print(f"   🔄 Атак на поток: 10") 
        print(f"   🎯 Эндпоинтов: 10 (WebAccountApi: 3, WebAccountV2Api: 4, WebDirectoryApi: 3)")
        print(f"   📝 Всего запросов: {5 * 10 * 10} (5 потоков × 10 атак × 10 эндпоинтов)")
        print("🔥 НАЧИНАЕМ НАГРУЗОЧНОЕ ТЕСТИРОВАНИЕ...")
        
        start_time = time.time()
        
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(self.worker_thread, thread_id) for thread_id in range(1, 6)]
            for future in futures:
                future.result()
        
        end_time = time.time()
        total_time = end_time - start_time
        
        print(f"\n⏱️ Общее время выполнения: {total_time:.2f} секунд")
        print("💾 Сохраняем статистику по потокам в Excel...")
        
        self.save_to_excel()
        
        print("\n🏁 НАГРУЗОЧНЫЙ ТЕСТ ЗАВЕРШЕН")
        print("=" * 50)

if __name__ == "__main__":
    EnvoyLoadTester().run_load_test()