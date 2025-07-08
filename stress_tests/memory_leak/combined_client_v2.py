#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WebAccountV2 API клиент с метриками и Excel экспортом
Выполняет 4 endpoint'а WebAccountV2Api по 1 разу каждый для тестирования
"""

import grpc
import json
import uuid
import sys
import os
import time
import pandas as pd
from datetime import datetime

sys.path.append(os.path.abspath("C:\\project_kicb\\stress_tests\\memory_leak"))
from protofile_pb2_grpc import WebAccountV2ApiStub
from protofile_pb2 import WebAccountsRequest

class WebAccountV2Client:
    def __init__(self):
        # Настройки подключения
        options = [
            ('grpc.max_receive_message_length', -1),
            ('grpc.max_send_message_length', -1),
        ]
        
        # Подключение к серверу
        self.channel = grpc.secure_channel('newibanktest.kicb.net:443', grpc.ssl_channel_credentials(), options)
        self.stub = WebAccountV2ApiStub(self.channel)
        
        # Сессионные данные (по JS примеру)
        self.session_data = {
            'sessionKey': '5MtEKcQbp3LZZXK5s3lNIH',      # Обновленный ключ
            'device-type': 'ios',
            'x-real-ip': '138.199.55.230',
            'user-agent': '{"ua": {"device": "iPhone 15 Pro", "osVersion": "18.0.1"}, "imei": "9C2F553F-06EB-42C2-AF92-5D3BBF9304E1", "deviceName": "", "deviceType": "ios", "macAddress": "9C2F553F-06EB-42C2-AF92-5D3BBF9304E1"}',
            'user-agent-c': '18.0.1; iPhone 15 Pro',   # Как в JS примере
            'app-type': 'I'
        }
        
        # Список для сбора метрик
        self.metrics = []
    
    def get_metadata(self):
        # По JS примеру, но ключи в lowercase для Python gRPC
        return [
            ('sessionkey', self.session_data['sessionKey']),     # sessionKey → sessionkey
            ('device-type', self.session_data['device-type']),
            ('refid', str(uuid.uuid4())),                   # refId → refid  
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
    
    def _record_metric(self, endpoint, start_time, end_time, request_size, response_size, success, data_length, error=None, iteration=1):
        """Записывает метрику"""
        metric = {
            'timestamp': datetime.fromtimestamp(start_time).strftime('%Y-%m-%d %H:%M:%S.%f')[:-3],
            'endpoint': endpoint,
            'iteration': iteration,
            'api_type': 'WebAccountV2',
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
        status_icon = "✅" if success else "❌"
        print(f"   {status_icon} Попытка {iteration}: {end_time - start_time:.3f}с, {request_size + response_size} bytes, {data_length} символов")

    def send_request(self, endpoint, data=None, iteration=1):
        if data is None:
            data = {}
        
        request = WebAccountsRequest(code=endpoint, data=json.dumps(data))
        metadata = self.get_metadata()
        
        # Вычисляем размер запроса
        request_size = self._calculate_request_size(request, metadata)
        
        start_time = time.time()
        try:
            response = self.stub.makeWebAccountV2(request, metadata=metadata)
            end_time = time.time()
            
            # Вычисляем размер ответа
            response_size = self._calculate_response_size(response)
            success = response.success
            data_length = len(response.data) if response.success and response.data else 0
            error = response.error.code if not response.success else None
            
            # Записываем метрику
            self._record_metric(endpoint, start_time, end_time, request_size, response_size, success, data_length, error, iteration)
            
            return {
                'success': success,
                'data': response.data if success else None,
                'error': error,
                'duration': end_time - start_time
            }
        except Exception as e:
            end_time = time.time()
            # Записываем метрику для ошибки
            self._record_metric(endpoint, start_time, end_time, request_size, 0, False, 0, str(e), iteration)
            return {
                'success': False,
                'data': None,
                'error': str(e),
                'duration': end_time - start_time
            }

    def test_endpoints_multiple_times(self, iterations=1):
        """Тестирует все endpoint'ы указанное количество раз"""
        endpoints = [
            ('GET_LIST_OF_STORIES', {}),
            ('GET_ACCOUNTS', {'accountStatus': 'O'}),
            ('GET_EXCHANGE_RATE', {'rateType': 'cash'}),
            ('GET_LIST_OF_TEMPLATES', {'pageNumber': 1, 'pageSize': 20, 'templateName': ''})
        ]
        
        results_summary = {}
        
        print(f"=== WebAccountV2 API Тест ({iterations} итерация) ===\n")
        
        for endpoint, data in endpoints:
            print(f"\n🎯 Тестируем {endpoint} ({iterations} раз):")
            
            endpoint_results = []
            successful_count = 0
            total_duration = 0
            
            for i in range(1, iterations + 1):
                result = self.send_request(endpoint, data, iteration=i)
                endpoint_results.append(result)
                
                if result['success']:
                    successful_count += 1
                    total_duration += result['duration']
                
                # Небольшая пауза между запросами
                if i < iterations:
                    time.sleep(0.1)
            
            # Вычисляем статистику
            avg_duration = total_duration / successful_count if successful_count > 0 else 0
            success_rate = (successful_count / iterations) * 100
            
            results_summary[endpoint] = {
                'total_requests': iterations,
                'successful_requests': successful_count,
                'failed_requests': iterations - successful_count,
                'success_rate': success_rate,
                'average_duration': avg_duration,
                'total_duration': total_duration
            }
            
            print(f"   📊 Успешно: {successful_count}/{iterations} ({success_rate:.1f}%)")
            if successful_count > 0:
                print(f"   ⏱️ Среднее время: {avg_duration:.3f} секунд")
        
        return results_summary
    
    def export_metrics_to_excel(self, filename=None):
        """Экспортирует метрики в Excel файл"""
        if not self.metrics:
            print("❌ Нет метрик для экспорта")
            return None
            
        if filename is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'webaccountv2_metrics_{timestamp}.xlsx'
        
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
            
            print(f"\n✅ Метрики экспортированы в: {filename}")
            print(f"📊 Общий network usage: {total_network:,} bytes")
            print(f"📊 Общий объем данных с бэка: {total_backend_data:,} символов")
            print(f"📊 Общее время выполнения: {total_time:.3f} секунд")
            print(f"📊 Успешность: {success_rate:.1f}%")
            
            return filename
            
        except Exception as e:
            print(f"❌ Ошибка при экспорте в Excel: {e}")
            return None

    def close(self):
        """Закрывает соединение"""
        if hasattr(self, 'channel'):
            self.channel.close()

if __name__ == "__main__":
    client = WebAccountV2Client()
    try:
        # Выполняем тесты с 1 итерацией
        results = client.test_endpoints_multiple_times(iterations=1)
        
        # Выводим общую сводку
        print(f"\n=== ОБЩАЯ СВОДКА ===")
        total_requests = sum(r['total_requests'] for r in results.values())
        total_successful = sum(r['successful_requests'] for r in results.values())
        overall_success_rate = (total_successful / total_requests) * 100 if total_requests > 0 else 0
        
        print(f"Общее количество запросов: {total_requests}")
        print(f"Успешных запросов: {total_successful}")
        print(f"Общая успешность: {overall_success_rate:.1f}%")
        
        print(f"\n=== ДЕТАЛИЗАЦИЯ ПО ENDPOINT'АМ ===")
        for endpoint, stats in results.items():
            print(f"{endpoint}:")
            print(f"  Успешность: {stats['successful_requests']}/{stats['total_requests']} ({stats['success_rate']:.1f}%)")
            if stats['successful_requests'] > 0:
                print(f"  Среднее время: {stats['average_duration']:.3f} секунд")
        
        # Экспортируем метрики в Excel
        print(f"\n=== ЭКСПОРТ МЕТРИК ===")
        excel_file = client.export_metrics_to_excel()
        
    finally:
        client.close() 