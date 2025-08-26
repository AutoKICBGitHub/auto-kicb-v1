#!/usr/bin/env python3
import grpc
import json
import uuid
import sys
import os
import time
import requests
import threading
from datetime import datetime
import pandas as pd

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from protofile_pb2_grpc import WebAccountApiStub, WebAccountV2ApiStub, WebDirectoryApiStub
from protofile_pb2 import WebAccountsRequest, IncomingWebDirectory

class EnvoyLoadTester:
    def __init__(self):
        self.server = 'remote.kicb.net:443'
        self.options = [('grpc.max_receive_message_length', -1), ('grpc.max_send_message_length', -1)]
        self.requests_per_api = 333
        self.session_data = {
            'sessionKey': '2cDOGN1zB4Ys4cXG0g2xii',
            'sessionId': '0Ac0BF35veDHYjCgfUwETc',
            'device-type': 'ios',
            'x-real-ip': '93.170.8.20',
            'user-agent': '{"ua": {"device": "iPhone X", "osVersion": "16.7.7"}, "imei": "A428AB95-421E-4D78-9A86-0D6BDB1E39C6", "deviceName": "", "deviceType": "ios", "macAddress": "A428AB95-421E-4D78-9A86-0D6BDB1E39C6"}',
            'user-agent-c': '16.7.7; iPhone X',
            'app-type': 'I',
            'imei': 'A428AB95-421E-4D78-9A86-0D6BDB1E39C6',
            'userId': '131906'
        }
        self.results = []  # Детальные результаты по каждому запросу
        self.api_stats = {}  # Статистика по каждой API
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
    
    def init_api_stats(self, api_name: str):
        """Инициализирует статистику для API"""
        if api_name not in self.api_stats:
            self.api_stats[api_name] = {
                'api_name': api_name,
                'start_time': datetime.now(),
                'end_time': None,
                'internet_speed_start': self.measure_internet_speed(),
                'internet_speed_end': 0,
                'total_requests': 0,
                'successful_requests': 0,
                'failed_requests': 0,
                'response_times': [],
                'per_endpoint': {}
            }

    def record_result(self, api_name, endpoint, start_time, end_time, success, error_code=None, response_size=0):
        """Записывает результат запроса и обновляет статистику API"""
        response_time_ms = round((end_time - start_time) * 1000, 2)

        # Детальный лог
        with self.lock:
            self.results.append({
                'timestamp': datetime.fromtimestamp(start_time).strftime('%Y-%m-%d %H:%M:%S.%f')[:-3],
                'api_name': api_name,
                'endpoint': endpoint,
                'response_time_ms': response_time_ms,
                'success': success,
                'error_code': error_code,
                'response_size_bytes': response_size
            })

        # Статистика по API
        self.init_api_stats(api_name)
        with self.lock:
            stats = self.api_stats[api_name]
            stats['total_requests'] += 1
            stats['response_times'].append(response_time_ms)
            if success:
                stats['successful_requests'] += 1
            else:
                stats['failed_requests'] += 1

            # По эндпоинту
            if endpoint not in stats['per_endpoint']:
                stats['per_endpoint'][endpoint] = {
                    'requests': 0,
                    'success': 0,
                    'response_times': []
                }
            ep = stats['per_endpoint'][endpoint]
            ep['requests'] += 1
            if success:
                ep['success'] += 1
            ep['response_times'].append(response_time_ms)
    
    def log_error(self, api_name, endpoint, error_message):
        """Записывает ошибку в список и выводит в консоль"""
        error_info = {
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3],
            'api_name': api_name,
            'endpoint': endpoint,
            'error_message': str(error_message)
        }
        with self.lock:
            self.errors.append(error_info)
        # Выводим ошибку в консоль сразу
        print(f"❌ {api_name}.{endpoint}: {error_message}")
        
        return str(error_message)

    def finalize_api_stats(self, api_name: str):
        """Финализирует статистику по API"""
        if api_name in self.api_stats:
            stats = self.api_stats[api_name]
            stats['end_time'] = datetime.now()
            stats['internet_speed_end'] = self.measure_internet_speed()

            # Фильтруем только успешные запросы для расчёта времени ответа
            successful_times = [t for i, t in enumerate(stats['response_times']) 
                              if i < stats['successful_requests']]
            if successful_times:
                stats['avg_response_time'] = round(sum(successful_times) / len(successful_times), 2)
                stats['min_response_time'] = round(min(successful_times), 2)
                stats['max_response_time'] = round(max(successful_times), 2)
            else:
                stats['avg_response_time'] = 0
                stats['min_response_time'] = 0
                stats['max_response_time'] = 0

            total = stats['total_requests']
            succ = stats['successful_requests']
            stats['success_rate'] = round((succ / total) * 100, 2) if total > 0 else 0
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

    def _call_webaccount_api(self, stub: WebAccountApiStub, endpoint: str):
        start_time = time.time()
        try:
            data = {"userId": int(self.session_data['userId'])}
            request = WebAccountsRequest(code=endpoint, data=json.dumps(data))
            metadata = self.get_session_metadata()
            response = stub.makeWebAccount(request, metadata=metadata)
            end_time = time.time()

            if response.success:
                response_size = len(response.data) if hasattr(response, 'data') and response.data else 0
                return True, start_time, end_time, None, response_size
            else:
                error_code = response.error.code if response.error else "UNKNOWN_ERROR"
                error_msg = response.error.message if response.error and hasattr(response.error, 'message') else "Неизвестная ошибка сервера"
                full_error = f"{error_code}: {error_msg}"
                return False, start_time, end_time, full_error, 0
        except Exception as e:
            end_time = time.time()
            return False, start_time, end_time, f"Exception: {str(e)}", 0

    def _schedule_webaccount_api(self, stub: WebAccountApiStub, endpoint: str):
        """Планирует асинхронный вызов WebAccountApi и возвращает (future, start_time, endpoint)"""
        start_time = time.time()
        data = {"userId": int(self.session_data['userId'])}
        request = WebAccountsRequest(code=endpoint, data=json.dumps(data))
        metadata = self.get_session_metadata()
        future = stub.makeWebAccount.future(request, metadata=metadata)
        return future, start_time, endpoint

    def _call_webaccount_v2_api(self, stub: WebAccountV2ApiStub, endpoint: str, payload_template: dict):
        start_time = time.time()
        try:
            data = dict(payload_template)
            data['userId'] = int(self.session_data['userId'])
            data['sessionId'] = self.session_data['sessionId']
            request = WebAccountsRequest(code=endpoint, data=json.dumps(data))
            metadata = self.get_v2_metadata()
            response = stub.makeWebAccountV2(request, metadata=metadata)
            end_time = time.time()

            if response.success:
                response_size = len(response.data) if hasattr(response, 'data') and response.data else 0
                return True, start_time, end_time, None, response_size
            else:
                error_code = response.error.code if response.error else "UNKNOWN_ERROR"
                error_msg = response.error.message if response.error and hasattr(response.error, 'message') else "Неизвестная ошибка сервера"
                full_error = f"{error_code}: {error_msg}"
                return False, start_time, end_time, full_error, 0
        except Exception as e:
            end_time = time.time()
            return False, start_time, end_time, f"Exception: {str(e)}", 0

    def _schedule_webaccount_v2_api(self, stub: WebAccountV2ApiStub, endpoint: str, payload_template: dict):
        """Планирует асинхронный вызов WebAccountV2Api и возвращает (future, start_time, endpoint)"""
        start_time = time.time()
        data = dict(payload_template)
        data['userId'] = int(self.session_data['userId'])
        data['sessionId'] = self.session_data['sessionId']
        request = WebAccountsRequest(code=endpoint, data=json.dumps(data))
        metadata = self.get_v2_metadata()
        future = stub.makeWebAccountV2.future(request, metadata=metadata)
        return future, start_time, endpoint

    def _call_webdirectory_api(self, stub: WebDirectoryApiStub, endpoint: str):
        start_time = time.time()
        try:
            request = IncomingWebDirectory(code=endpoint, data=None)
            metadata = self.get_basic_metadata()
            response = stub.makeWebDirectory(request, metadata=metadata)
            end_time = time.time()

            if response.data and len(response.data) > 0:
                response_size = len(response.data)
                return True, start_time, end_time, None, response_size
            else:
                return False, start_time, end_time, "EMPTY_RESPONSE: Сервер вернул пустой ответ", 0
        except Exception as e:
            end_time = time.time()
            return False, start_time, end_time, f"Exception: {str(e)}", 0

    def _schedule_webdirectory_api(self, stub: WebDirectoryApiStub, endpoint: str):
        """Планирует асинхронный вызов WebDirectoryApi и возвращает (future, start_time, endpoint)"""
        start_time = time.time()
        request = IncomingWebDirectory(code=endpoint, data=None)
        metadata = self.get_basic_metadata()
        future = stub.makeWebDirectory.future(request, metadata=metadata)
        return future, start_time, endpoint


    def run_webaccount_api_sequential(self, rps: int = 8):
        api_name = 'WebAccountApi'
        endpoints = ['GET_ACCOUNTS', 'GET_LOANS', 'GET_DEPOSITS']
        self.init_api_stats(api_name)
        channel = grpc.secure_channel(self.server, grpc.ssl_channel_credentials(), self.options)
        stub = WebAccountApiStub(channel)
        interval = 1.0 / max(1, rps)
        next_time = time.perf_counter()
        futures = []
        for i in range(self.requests_per_api):
            now = time.perf_counter()
            if now < next_time:
                time.sleep(next_time - now)
                next_time += interval
            else:
                next_time = now + interval
            endpoint = endpoints[i % len(endpoints)]
            future, start_ts, ep = self._schedule_webaccount_api(stub, endpoint)
            def _cb(fut, api=api_name, endpoint=ep, start=start_ts):
                end_ts = time.time()
                try:
                    response = fut.result()
                    if getattr(response, 'success', False):
                        response_size = len(response.data) if hasattr(response, 'data') and response.data else 0
                        self.record_result(api, endpoint, start, end_ts, True, response_size=response_size)
                    else:
                        error_code = response.error.code if getattr(response, 'error', None) else "UNKNOWN_ERROR"
                        error_msg = getattr(getattr(response, 'error', None), 'message', '') or "Неизвестная ошибка сервера"
                        logged_error = self.log_error(api, endpoint, f"{error_code}: {error_msg}")
                        self.record_result(api, endpoint, start, end_ts, False, error_code=logged_error)
                except Exception as e:
                    logged_error = self.log_error(api, endpoint, f"Exception: {str(e)}")
                    self.record_result(api, endpoint, start, end_ts, False, error_code=logged_error)
            future.add_done_callback(_cb)
            futures.append(future)
        # Дождаться завершения всех future
        for fut in futures:
            try:
                fut.result()
            except Exception:
                pass
        channel.close()
        self.finalize_api_stats(api_name)

    def run_webaccount_v2_api_sequential(self, rps: int = 8):
        api_name = 'WebAccountV2Api'
        endpoints_tpls = [
            ('GET_LIST_OF_STORIES', {}),
            ('GET_ACCOUNTS', {'accountStatus': 'O'}),
            ('GET_EXCHANGE_RATE', {'rateType': 'cash'}),
            ('GET_LIST_OF_TEMPLATES', {'pageNumber': 1, 'pageSize': 20, 'templateName': ''})
        ]
        endpoints = [code for code, _ in endpoints_tpls]
        templates = {code: tpl for code, tpl in endpoints_tpls}
        self.init_api_stats(api_name)
        channel = grpc.secure_channel(self.server, grpc.ssl_channel_credentials(), self.options)
        stub = WebAccountV2ApiStub(channel)
        interval = 1.0 / max(1, rps)
        next_time = time.perf_counter()
        futures = []
        for i in range(self.requests_per_api):
            now = time.perf_counter()
            if now < next_time:
                time.sleep(next_time - now)
                next_time += interval
            else:
                next_time = now + interval
            endpoint = endpoints[i % len(endpoints)]
            tpl = templates.get(endpoint, {})
            future, start_ts, ep = self._schedule_webaccount_v2_api(stub, endpoint, tpl)
            def _cb(fut, api=api_name, endpoint=ep, start=start_ts):
                end_ts = time.time()
                try:
                    response = fut.result()
                    if getattr(response, 'success', False):
                        response_size = len(response.data) if hasattr(response, 'data') and response.data else 0
                        self.record_result(api, endpoint, start, end_ts, True, response_size=response_size)
                    else:
                        error_code = response.error.code if getattr(response, 'error', None) else "UNKNOWN_ERROR"
                        error_msg = getattr(getattr(response, 'error', None), 'message', '') or "Неизвестная ошибка сервера"
                        logged_error = self.log_error(api, endpoint, f"{error_code}: {error_msg}")
                        self.record_result(api, endpoint, start, end_ts, False, error_code=logged_error)
                except Exception as e:
                    logged_error = self.log_error(api, endpoint, f"Exception: {str(e)}")
                    self.record_result(api, endpoint, start, end_ts, False, error_code=logged_error)
            future.add_done_callback(_cb)
            futures.append(future)
        for fut in futures:
            try:
                fut.result()
            except Exception:
                pass
        channel.close()
        self.finalize_api_stats(api_name)

    def run_webdirectory_api_sequential(self, rps: int = 8):
        api_name = 'WebDirectoryApi'
        endpoints = ['GET_DIRECTORY_EXCHANGE_RATES', 'GET_DV_OF_DIRECTORIES', 'GET_DIRECTORY_BRANCHES_ATMS']
        self.init_api_stats(api_name)
        channel = grpc.secure_channel(self.server, grpc.ssl_channel_credentials(), self.options)
        stub = WebDirectoryApiStub(channel)
        interval = 1.0 / max(1, rps)
        next_time = time.perf_counter()
        futures = []
        for i in range(self.requests_per_api):
            now = time.perf_counter()
            if now < next_time:
                time.sleep(next_time - now)
                next_time += interval
            else:
                next_time = now + interval
            endpoint = endpoints[i % len(endpoints)]
            future, start_ts, ep = self._schedule_webdirectory_api(stub, endpoint)
            def _cb(fut, api=api_name, endpoint=ep, start=start_ts):
                end_ts = time.time()
                try:
                    response = fut.result()
                    if getattr(response, 'data', None) and len(response.data) > 0:
                        response_size = len(response.data)
                        self.record_result(api, endpoint, start, end_ts, True, response_size=response_size)
                    else:
                        logged_error = self.log_error(api, endpoint, "EMPTY_RESPONSE: Сервер вернул пустой ответ")
                        self.record_result(api, endpoint, start, end_ts, False, error_code=logged_error)
                except Exception as e:
                    logged_error = self.log_error(api, endpoint, f"Exception: {str(e)}")
                    self.record_result(api, endpoint, start, end_ts, False, error_code=logged_error)
            future.add_done_callback(_cb)
            futures.append(future)
        for fut in futures:
            try:
                fut.result()
            except Exception:
                pass
        channel.close()
        self.finalize_api_stats(api_name)

    def run_all_apis_concurrent(self, rps_per_api: int = 8):
        """Одновременная отправка заданного количества запросов в каждую из 3 API с заданным RPS на каждую API."""
        wa_name = 'WebAccountApi'
        v2_name = 'WebAccountV2Api'
        wd_name = 'WebDirectoryApi'

        # Инициализация статистики
        self.init_api_stats(wa_name)
        self.init_api_stats(v2_name)
        self.init_api_stats(wd_name)

        # Каналы и стабы
        wa_channel = grpc.secure_channel(self.server, grpc.ssl_channel_credentials(), self.options)
        wa_stub = WebAccountApiStub(wa_channel)

        v2_channel = grpc.secure_channel(self.server, grpc.ssl_channel_credentials(), self.options)
        v2_stub = WebAccountV2ApiStub(v2_channel)

        wd_channel = grpc.secure_channel(self.server, grpc.ssl_channel_credentials(), self.options)
        wd_stub = WebDirectoryApiStub(wd_channel)

        # Эндпоинты и шаблоны
        wa_endpoints = ['GET_ACCOUNTS', 'GET_LOANS', 'GET_DEPOSITS']
        v2_tpls = [
            ('GET_LIST_OF_STORIES', {}),
            ('GET_ACCOUNTS', {'accountStatus': 'O'}),
            ('GET_EXCHANGE_RATE', {'rateType': 'cash'}),
            ('GET_LIST_OF_TEMPLATES', {'pageNumber': 1, 'pageSize': 20, 'templateName': ''})
        ]
        v2_endpoints = [code for code, _ in v2_tpls]
        v2_templates = {code: tpl for code, tpl in v2_tpls}
        wd_endpoints = ['GET_DIRECTORY_EXCHANGE_RATES', 'GET_DV_OF_DIRECTORIES', 'GET_DIRECTORY_BRANCHES_ATMS']

        # Планировщики RPS
        interval = 1.0 / max(1, rps_per_api)
        next_time = {
            wa_name: time.perf_counter(),
            v2_name: time.perf_counter(),
            wd_name: time.perf_counter(),
        }
        sent = {wa_name: 0, v2_name: 0, wd_name: 0}
        idx = {wa_name: 0, v2_name: 0, wd_name: 0}
        scheduled = []  # элементы: {api, endpoint, start_time, future}

        # Фаза отправки
        while sent[wa_name] < self.requests_per_api or sent[v2_name] < self.requests_per_api or sent[wd_name] < self.requests_per_api:
            now = time.perf_counter()

            if sent[wa_name] < self.requests_per_api and now >= next_time[wa_name]:
                ep = wa_endpoints[idx[wa_name] % len(wa_endpoints)]
                fut, start_ts, endpoint = self._schedule_webaccount_api(wa_stub, ep)
                def _cb(f, api=wa_name, endpoint=endpoint, start=start_ts):
                    end_ts = time.time()
                    try:
                        response = f.result()
                        if getattr(response, 'success', False):
                            response_size = len(response.data) if hasattr(response, 'data') and response.data else 0
                            self.record_result(api, endpoint, start, end_ts, True, response_size=response_size)
                        else:
                            error_code = response.error.code if getattr(response, 'error', None) else "UNKNOWN_ERROR"
                            error_msg = getattr(getattr(response, 'error', None), 'message', '') or "Неизвестная ошибка сервера"
                            logged_error = self.log_error(api, endpoint, f"{error_code}: {error_msg}")
                            self.record_result(api, endpoint, start, end_ts, False, error_code=logged_error)
                    except Exception as e:
                        logged_error = self.log_error(api, endpoint, f"Exception: {str(e)}")
                        self.record_result(api, endpoint, start, end_ts, False, error_code=logged_error)
                fut.add_done_callback(_cb)
                scheduled.append(fut)
                sent[wa_name] += 1
                idx[wa_name] += 1
                next_time[wa_name] += interval

            if sent[v2_name] < self.requests_per_api and now >= next_time[v2_name]:
                ep = v2_endpoints[idx[v2_name] % len(v2_endpoints)]
                tpl = v2_templates.get(ep, {})
                fut, start_ts, endpoint = self._schedule_webaccount_v2_api(v2_stub, ep, tpl)
                def _cb(f, api=v2_name, endpoint=endpoint, start=start_ts):
                    end_ts = time.time()
                    try:
                        response = f.result()
                        if getattr(response, 'success', False):
                            response_size = len(response.data) if hasattr(response, 'data') and response.data else 0
                            self.record_result(api, endpoint, start, end_ts, True, response_size=response_size)
                        else:
                            error_code = response.error.code if getattr(response, 'error', None) else "UNKNOWN_ERROR"
                            error_msg = getattr(getattr(response, 'error', None), 'message', '') or "Неизвестная ошибка сервера"
                            logged_error = self.log_error(api, endpoint, f"{error_code}: {error_msg}")
                            self.record_result(api, endpoint, start, end_ts, False, error_code=logged_error)
                    except Exception as e:
                        logged_error = self.log_error(api, endpoint, f"Exception: {str(e)}")
                        self.record_result(api, endpoint, start, end_ts, False, error_code=logged_error)
                fut.add_done_callback(_cb)
                scheduled.append(fut)
                sent[v2_name] += 1
                idx[v2_name] += 1
                next_time[v2_name] += interval

            if sent[wd_name] < self.requests_per_api and now >= next_time[wd_name]:
                ep = wd_endpoints[idx[wd_name] % len(wd_endpoints)]
                fut, start_ts, endpoint = self._schedule_webdirectory_api(wd_stub, ep)
                def _cb(f, api=wd_name, endpoint=endpoint, start=start_ts):
                    end_ts = time.time()
                    try:
                        response = f.result()
                        if getattr(response, 'data', None) and len(response.data) > 0:
                            response_size = len(response.data)
                            self.record_result(api, endpoint, start, end_ts, True, response_size=response_size)
                        else:
                            logged_error = self.log_error(api, endpoint, "EMPTY_RESPONSE: Сервер вернул пустой ответ")
                            self.record_result(api, endpoint, start, end_ts, False, error_code=logged_error)
                    except Exception as e:
                        logged_error = self.log_error(api, endpoint, f"Exception: {str(e)}")
                        self.record_result(api, endpoint, start, end_ts, False, error_code=logged_error)
                fut.add_done_callback(_cb)
                scheduled.append(fut)
                sent[wd_name] += 1
                idx[wd_name] += 1
                next_time[wd_name] += interval

            if sent[wa_name] < self.requests_per_api or sent[v2_name] < self.requests_per_api or sent[wd_name] < self.requests_per_api:
                nearest = min(next_time[a] for a in [wa_name, v2_name, wd_name] if sent[a] < self.requests_per_api)
                sleep_for = max(0.0, min(0.01, nearest - time.perf_counter()))
                if sleep_for > 0:
                    time.sleep(sleep_for)

        # Фаза ожидания завершения всех запросов
        for fut in scheduled:
            try:
                fut.result()
            except Exception:
                pass

        # Закрываем каналы и финализируем статистику
        wa_channel.close()
        v2_channel.close()
        wd_channel.close()

        self.finalize_api_stats(wa_name)
        self.finalize_api_stats(v2_name)
        self.finalize_api_stats(wd_name)
    
    def save_to_excel(self):
        """Сохраняет статистику по API в Excel файл"""
        if not self.api_stats:
            print("Нет данных для сохранения")
            return

        # Сохраняем в той же папке где находится скрипт
        script_dir = os.path.dirname(os.path.abspath(__file__))
        filename = os.path.join(script_dir, f"api_stats_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx")

        with pd.ExcelWriter(filename, engine='openpyxl') as writer:
            # СТАТИСТИКА ПО API
            api_rows = []
            for api_name, stats in self.api_stats.items():
                api_rows.append({
                    'API': api_name,
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

            pd.DataFrame(api_rows).to_excel(writer, sheet_name='Статистика по API', index=False)

            # ДЕТАЛИ ПО ЭНДПОИНТАМ
            endpoint_rows = []
            for api_name, stats in self.api_stats.items():
                for endpoint, ep_stats in stats['per_endpoint'].items():
                    # Фильтруем только успешные запросы для расчёта времени ответа
                    successful_times = [t for i, t in enumerate(ep_stats['response_times']) 
                                    if i < ep_stats['success']]
                    if successful_times:
                        avg_time = round(sum(successful_times) / len(successful_times), 2)
                        min_time = round(min(successful_times), 2)
                        max_time = round(max(successful_times), 2)
                    else:
                        avg_time = min_time = max_time = 0
                    success_rate = round((ep_stats['success'] / ep_stats['requests']) * 100, 2) if ep_stats['requests'] > 0 else 0
                    endpoint_rows.append({
                        'API': api_name,
                        'Эндпоинт': endpoint,
                        'Всего запросов': ep_stats['requests'],
                        'Успешных': ep_stats['success'],
                        'Процент успеха (%)': success_rate,
                        'Среднее время ответа (мс)': avg_time,
                        'Минимальное время (мс)': min_time,
                        'Максимальное время (мс)': max_time,
                    })
            pd.DataFrame(endpoint_rows).to_excel(writer, sheet_name='Детализация по эндпоинтам', index=False)

            # ОБЩАЯ СВОДКА
            total_requests = sum(stats['total_requests'] for stats in self.api_stats.values())
            total_successful = sum(stats['successful_requests'] for stats in self.api_stats.values())
            avg_internet_speed_start = round(sum(stats['internet_speed_start'] for stats in self.api_stats.values()) / len(self.api_stats), 2)
            avg_internet_speed_end = round(sum(stats['internet_speed_end'] for stats in self.api_stats.values()) / len(self.api_stats), 2)

            # Собираем только успешные времена ответа
            all_successful_times = []
            for stats in self.api_stats.values():
                successful_times = [t for i, t in enumerate(stats['response_times']) 
                                if i < stats['successful_requests']]
                all_successful_times.extend(successful_times)

            summary_data = [{
                'Параметр': 'Количество API',
                'Значение': len(self.api_stats)
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
                'Значение': round(sum(all_successful_times) / len(all_successful_times), 2) if all_successful_times else 0
            }, {
                'Параметр': 'Минимальное время ответа (мс)',
                'Значение': round(min(all_successful_times), 2) if all_successful_times else 0
            }, {
                'Параметр': 'Максимальное время ответа (мс)',
                'Значение': round(max(all_successful_times), 2) if all_successful_times else 0
            }, {
                'Параметр': 'Средняя скорость интернета в начале (КБ/с)',
                'Значение': avg_internet_speed_start
            }, {
                'Параметр': 'Средняя скорость интернета в конце (КБ/с)',
                'Значение': avg_internet_speed_end
            }]

            pd.DataFrame(summary_data).to_excel(writer, sheet_name='Общая сводка', index=False)

            # ОШИБКИ
            if self.errors:
                pd.DataFrame(self.errors).to_excel(writer, sheet_name='Ошибки', index=False)

        print(f"✅ Статистика по API сохранена в файл: {os.path.basename(filename)}")
        print(f"📁 Полный путь: {filename}")

        # Краткая статистика в консоль
        print(f"\n📊 РЕЗУЛЬТАТЫ НАГРУЗОЧНОГО ТЕСТА:")
        print(f"   API: {', '.join(self.api_stats.keys())}")
        print(f"   📝 Всего запросов: {sum(s['total_requests'] for s in self.api_stats.values())}")
        print(f"   ✅ Успешных: {sum(s['successful_requests'] for s in self.api_stats.values())}")
        print(f"   ❌ Ошибок: {len(self.errors)}")

    def run_load_test(self):
        print("🚀 ЗАПУСК НАГРУЗОЧНОГО ТЕСТА ENVOY")
        print("=" * 50)
        print("📊 Параметры теста:")
        print(f"   🔄 Запросов на API: {self.requests_per_api}")
        print("   ⚙️ Режим: одновременная нагрузка 3 API по 8 rps каждая")
        print("🔥 НАЧИНАЕМ НАГРУЗОЧНОЕ ТЕСТИРОВАНИЕ...")

        start_time = time.time()

        # Одновременная нагрузка всех трех API по 8 rps на каждую
        self.run_all_apis_concurrent(rps_per_api=8)

        end_time = time.time()
        total_time = end_time - start_time

        print(f"\n⏱️ Общее время выполнения: {total_time:.2f} секунд")
        print("💾 Сохраняем статистику в Excel...")

        self.save_to_excel()

        print("\n🏁 НАГРУЗОЧНЫЙ ТЕСТ ЗАВЕРШЕН")
        print("=" * 50)

if __name__ == "__main__":
    EnvoyLoadTester().run_load_test()