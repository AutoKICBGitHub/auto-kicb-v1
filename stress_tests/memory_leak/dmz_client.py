#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Простой клиент для DMZ API
Без проверок, максимально быстрый и легкий
"""

import grpc
import json
import uuid
import sys
import os

# Добавляем путь к протофайлу
sys.path.append(os.path.abspath("C:\\project_kicb\\stress_tests\\memory_leak"))

from protofile_pb2_grpc import WebDirectoryApiStub
from protofile_pb2 import IncomingWebDirectory

class DmzClient:
    def __init__(self):
        # Подключение к DMZ API (без указания порта - используется 443 по умолчанию)
        options = [
            ('grpc.max_receive_message_length', -1),
            ('grpc.max_send_message_length', -1),
        ]
        self.channel = grpc.secure_channel('newibanktest.kicb.net:443', grpc.ssl_channel_credentials(), options)
        self.stub = WebDirectoryApiStub(self.channel)
        
        # Правильные DMZ endpoints из JS кода
        self.endpoints = [
            'GET_DIRECTORY_EXCHANGE_RATES',
            'GET_DV_OF_DIRECTORIES',
            'GET_DIRECTORY_AD_BLOCK_IOS',
            'GET_DIRECTORY_BRANCHES_ATMS'
        ]
    
    def _get_metadata(self):
        """Генерирует базовую метадату для DMZ запросов (как в JS коде)"""
        return [
            ('refid', str(uuid.uuid4())),
            ('device-type', 'ios')
        ]
    
    def call_endpoint(self, endpoint):
        """Вызывает DMZ endpoint и возвращает результат"""
        # В JS коде data: null, поэтому передаем None
        request = IncomingWebDirectory(code=endpoint, data=None)
        metadata = self._get_metadata()
        
        try:
            # Используем makeWebDirectory как в JS коде
            response = self.stub.makeWebDirectory(request, metadata=metadata)
            return {
                'success': response.success if hasattr(response, 'success') else bool(response.data),
                'data': response.data if response.data else None,
                'error': response.error.code if hasattr(response, 'error') and response.error else None
            }
        except Exception as e:
            return {
                'success': False,
                'data': None,
                'error': str(e)
            }
    
    def call_all_endpoints(self):
        """Вызывает все DMZ endpoints и возвращает результаты"""
        results = {}
        for endpoint in self.endpoints:
            results[endpoint] = self.call_endpoint(endpoint)
        return results
    
    def close(self):
        """Закрывает соединение"""
        if hasattr(self, 'channel'):
            self.channel.close()

if __name__ == "__main__":
    client = DmzClient()
    try:
        # Тестируем все DMZ endpoints
        results = client.call_all_endpoints()
        
        print("=== РЕЗУЛЬТАТЫ DMZ API ===")
        for endpoint, result in results.items():
            status = "✅" if result['success'] else "❌"
            data_len = len(result['data']) if result['data'] else 0
            error = f" - {result['error']}" if result['error'] else ""
            print(f"{status} {endpoint}: {data_len} символов{error}")
            
    finally:
        client.close() 