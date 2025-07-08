#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Объединенный клиент для работы с WebUtility и WebAccount API
Выполняет 4 запроса последовательно:
1. GET_SELF_USER_DATA - WebUtility API
2. GET_ACCOUNTS - WebAccount API
3. GET_DEPOSITS - WebAccount API
4. LIST_TEMPLATE - WebAccount API

Собирает метрики: network usage, размеры запросов/ответов, время выполнения
Экспортирует результаты в Excel
"""

import grpc
import json
import uuid
import sys
import os
import time
import pandas as pd
from datetime import datetime

# Добавляем путь к протофайлу
sys.path.append(os.path.abspath("C:\\project_kicb\\stress_tests\\memory_leak"))

from protofile_pb2_grpc import WebUtilityApiStub, WebAccountApiStub
from protofile_pb2 import IncomingWebUtility, WebAccountsRequest

class CombinedClient:
    def __init__(self):
        # Настройки подключения
        options = [
            ('grpc.max_receive_message_length', -1),
            ('grpc.max_send_message_length', -1),
        ]
        
        # Подключение к серверу
        self.channel = grpc.secure_channel('newibanktest.kicb.net:443', grpc.ssl_channel_credentials(), options)
        
        # Создаем стабы для разных API
        self.utility_stub = WebUtilityApiStub(self.channel)
        self.account_stub = WebAccountApiStub(self.channel)
        
        # Актуальные сессионные данные (из рабочего JS-примера)
        self.session_data = {
            'sessionKey': '5MtEKcQbp3LZZXK5s3lNIH',
            'sessionId': '5P2qfQVZcRGMldmHzyfAaI',
            'device-type': 'ios',
            'x-real-ip': '138.199.55.230',
            'user-agent': '{"ua": {"device": "iPhone 15 Pro", "osVersion": "18.0.1"}, "imei": "9C2F553F-06EB-42C2-AF92-5D3BBF9304E1", "deviceName": "", "deviceType": "ios", "macAddress": "9C2F553F-06EB-42C2-AF92-5D3BBF9304E1"}',
            'user-agent-c': '18.0.1; iPhone 15 Pro',
            'app-type': 'I'
        }
        
        # Список для сбора метрик
        self.metrics = []
    
    def _get_utility_metadata_js_style(self):
        """Метадата для WebUtility: все ключи lowercase для gRPC"""
        return [
            ('sessionkey', self.session_data['sessionKey']),
            ('refid', str(uuid.uuid4())),
            ('device-type', self.session_data['device-type']),
            ('user-agent-c', self.session_data['user-agent-c'])
        ]
    
    def _get_account_metadata(self):
        """Генерирует метадату для WebAccount запросов"""
        return [
            ('sessionkey', self.session_data['sessionKey']),
            ('sessionid', self.session_data['sessionId']),
            ('device-type', self.session_data['device-type']),
            ('refid', str(uuid.uuid4())),
            ('x-real-ip', self.session_data['x-real-ip']),
            ('user-agent', self.session_data['user-agent']),
            ('user-agent-c', self.session_data['user-agent-c']),
            ('app-type', self.session_data['app-type'])
        ]
    
    def _calculate_request_size(self, request, metadata):
        """Вычисляет размер запроса в байтах"""
        try:
            # Размер сериализованного протобуфа
            serialized_request = request.SerializeToString()
            request_size = len(serialized_request)
            
            # Размер метадаты (примерный)
            metadata_size = sum(len(str(key)) + len(str(value)) for key, value in metadata)
            
            return request_size + metadata_size
        except Exception:
            return 0
    
    def _calculate_response_size(self, response):
        """Вычисляет размер ответа в байтах"""
        try:
            if hasattr(response, 'data') and response.data:
                return len(response.data.encode('utf-8'))
            return 0
        except Exception:
            return 0
    
    def _record_metric(self, endpoint, api_type, start_time, end_time, request_size, response_size, success, data_length, error=None):
        """Записывает метрику"""
        metric = {
            'timestamp': datetime.fromtimestamp(start_time).strftime('%Y-%m-%d %H:%M:%S.%f')[:-3],
            'endpoint': endpoint,
            'api_type': api_type,
            'duration_seconds': round(end_time - start_time, 3),
            'request_size_bytes': request_size,
            'response_size_bytes': response_size,
            'total_network_bytes': request_size + response_size,
            'backend_data_length': data_length,
            'status': 'SUCCESS' if success else 'ERROR',
            'error_code': error if error else ''
        }
        self.metrics.append(metric)
        
        # Логируем метрику
        print(f"   📊 Метрика: {request_size + response_size} bytes network, {data_length} символов с бэка")
    
    def call_get_self_user_data(self):
        """Вызывает GET_SELF_USER_DATA через WebUtility API (только JS-style)"""
        request = IncomingWebUtility(code='GET_SELF_USER_DATA', data=json.dumps({}))
        metadata = self._get_utility_metadata_js_style()
        
        print('Request:', request)
        print('Metadata:', metadata)
        
        # Вычисляем размер запроса
        request_size = self._calculate_request_size(request, metadata)
        
        start_time = time.time()
        try:
            response = self.utility_stub.makeWebUtility(request, metadata=metadata)
            end_time = time.time()
            
            # Вычисляем размер ответа
            response_size = self._calculate_response_size(response)
            success = response.success if hasattr(response, 'success') else bool(response.data)
            data_length = len(response.data) if response.data else 0
            error = response.error.code if hasattr(response, 'error') and response.error else None
            
            # Записываем метрику
            self._record_metric('GET_SELF_USER_DATA', 'WebUtility', start_time, end_time, 
                              request_size, response_size, success, data_length, error)
            
            return {
                'success': success,
                'data': response.data if response.data else None,
                'error': error
            }
        except Exception as e:
            end_time = time.time()
            # Записываем метрику для ошибки
            self._record_metric('GET_SELF_USER_DATA', 'WebUtility', start_time, end_time, 
                              request_size, 0, False, 0, str(e))
            return {
                'success': False,
                'data': None,
                'error': str(e)
            }

    def call_webaccount_endpoint(self, endpoint):
        """Вызывает endpoint через WebAccount API"""
        request = WebAccountsRequest(code=endpoint, data=json.dumps({}))
        metadata = self._get_account_metadata()
        
        # Вычисляем размер запроса
        request_size = self._calculate_request_size(request, metadata)
        
        start_time = time.time()
        try:
            response = self.account_stub.makeWebAccount(request, metadata=metadata)
            end_time = time.time()
            
            # Вычисляем размер ответа
            response_size = self._calculate_response_size(response)
            success = response.success
            data_length = len(response.data) if response.success and response.data else 0
            error = response.error.code if not response.success else None
            
            # Записываем метрику
            self._record_metric(endpoint, 'WebAccount', start_time, end_time, 
                              request_size, response_size, success, data_length, error)
            
            return {
                'success': success,
                'data': response.data if success else None,
                'error': error
            }
        except Exception as e:
            end_time = time.time()
            # Записываем метрику для ошибки
            self._record_metric(endpoint, 'WebAccount', start_time, end_time, 
                              request_size, 0, False, 0, str(e))
            return {
                'success': False,
                'data': None,
                'error': str(e)
            }

    def execute_combined_requests(self):
        """Выполняет все 4 запроса последовательно"""
        results = {}
        print("=== ВЫПОЛНЕНИЕ ОБЪЕДИНЕННЫХ ЗАПРОСОВ ===")
        print(f"📊 Собираем метрики: network usage, размеры данных, время выполнения\n")
        
        # 1. GET_SELF_USER_DATA
        print(f"1. Выполняю GET_SELF_USER_DATA (utility API)...")
        result = self.call_get_self_user_data()
        status = "✅" if result['success'] else "❌"
        data_len = len(result['data']) if result['data'] else 0
        error_info = f" - {result['error']}" if result['error'] else ""
        print(f"   {status} {data_len} символов{error_info}")
        results['GET_SELF_USER_DATA'] = result
        
        # 2-4. WebAccount запросы
        webaccount_requests = ['GET_ACCOUNTS', 'GET_DEPOSITS', 'LIST_TEMPLATE']
        for i, endpoint in enumerate(webaccount_requests, 2):
            print(f"\n{i}. Выполняю {endpoint} (account API)...")
            result = self.call_webaccount_endpoint(endpoint)
            results[endpoint] = result
            status = "✅" if result['success'] else "❌"
            data_len = len(result['data']) if result['data'] else 0
            error_info = f" - {result['error']}" if result['error'] else ""
            print(f"   {status} {data_len} символов{error_info}")
            if i < len(webaccount_requests) + 1:
                time.sleep(0.1)
        
        return results
    
    def export_metrics_to_excel(self, filename=None):
        """Экспортирует метрики в Excel файл"""
        if not self.metrics:
            print("❌ Нет метрик для экспорта")
            return None
            
        if filename is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'combined_metrics_{timestamp}.xlsx'
        
        try:
            # Создаем DataFrame
            df = pd.DataFrame(self.metrics)
            
            # Сортируем по времени
            df = df.sort_values('timestamp')
            
            # Добавляем итоговые метрики
            total_network = df['total_network_bytes'].sum()
            total_backend_data = df['backend_data_length'].sum()
            total_time = df['duration_seconds'].sum()
            success_rate = (df['status'] == 'SUCCESS').mean() * 100
            
            # Статистика по endpoint'ам
            endpoint_stats = df.groupby('endpoint').agg({
                'duration_seconds': ['count', 'mean', 'std', 'min', 'max'],
                'total_network_bytes': 'sum',
                'backend_data_length': 'mean',
                'status': lambda x: (x == 'SUCCESS').mean() * 100
            }).round(3)
            
            # Создаем summary
            summary_data = {
                'metric': ['Total Network Usage (bytes)', 'Total Backend Data (chars)', 
                          'Total Time (seconds)', 'Success Rate (%)', 'Total Requests'],
                'value': [total_network, total_backend_data, round(total_time, 3), 
                         round(success_rate, 1), len(df)]
            }
            summary_df = pd.DataFrame(summary_data)
            
            # Сохраняем в Excel с тремя листами
            with pd.ExcelWriter(filename, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name='Detailed_Metrics', index=False)
                summary_df.to_excel(writer, sheet_name='Summary', index=False)
                endpoint_stats.to_excel(writer, sheet_name='Endpoint_Statistics')
            
            print(f"✅ Метрики экспортированы в: {filename}")
            print(f"📊 Общий network usage: {total_network:,} bytes")
            print(f"📊 Общий объем данных с бэка: {total_backend_data:,} символов")
            print(f"📊 Общее время выполнения: {total_time:.3f} секунд")
            print(f"📊 Успешность: {success_rate:.1f}%")
            
            return filename
            
        except Exception as e:
            print(f"❌ Ошибка при экспорте в Excel: {e}")
            return None

    def get_summary(self, results):
        """Возвращает сводку по результатам"""
        total_requests = len(results)
        successful_requests = sum(1 for r in results.values() if r['success'])
        failed_requests = total_requests - successful_requests
        
        total_data_size = sum(len(r['data']) if r['data'] else 0 for r in results.values())
        
        return {
            'total_requests': total_requests,
            'successful_requests': successful_requests,
            'failed_requests': failed_requests,
            'total_data_size': total_data_size,
            'success_rate': (successful_requests / total_requests) * 100 if total_requests > 0 else 0
        }
    
    def close(self):
        """Закрывает соединение"""
        if hasattr(self, 'channel'):
            self.channel.close()

if __name__ == "__main__":
    client = CombinedClient()
    try:
        # Выполняем объединенные запросы
        results = client.execute_combined_requests()
        
        # Выводим сводку
        summary = client.get_summary(results)
        
        print(f"\n=== СВОДКА ===")
        print(f"Общее количество запросов: {summary['total_requests']}")
        print(f"Успешных запросов: {summary['successful_requests']}")
        print(f"Неудачных запросов: {summary['failed_requests']}")
        print(f"Общий размер данных: {summary['total_data_size']} символов")
        print(f"Успешность: {summary['success_rate']:.1f}%")
        
        # Экспортируем метрики в Excel
        print(f"\n=== ЭКСПОРТ МЕТРИК ===")
        excel_file = client.export_metrics_to_excel()
        
        # Детализированные результаты
        print(f"\n=== ДЕТАЛИЗИРОВАННЫЕ РЕЗУЛЬТАТЫ ===")
        for endpoint, result in results.items():
            status = "✅ УСПЕШНО" if result['success'] else "❌ ОШИБКА"
            data_info = f"Данных: {len(result['data'])} символов" if result['data'] else "Данных нет"
            error_info = f"Ошибка: {result['error']}" if result['error'] else ""
            
            print(f"{endpoint}: {status}")
            print(f"  {data_info}")
            if error_info:
                print(f"  {error_info}")
            
    finally:
        client.close() 