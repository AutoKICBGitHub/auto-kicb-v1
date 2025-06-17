#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Простой клиент для WebAccount API
Без проверок, максимально быстрый и легкий
"""

import grpc
import json
import uuid
import sys
import os

# Добавляем путь к протофайлу
sys.path.append(os.path.abspath("C:\\project_kicb\\stress_tests\\memory_leak"))

from protofile_pb2_grpc import WebAccountApiStub
from protofile_pb2 import WebAccountsRequest

class WebAccountClient:
    def __init__(self):
        # Подключение
        self.channel = grpc.secure_channel('newibanktest.kicb.net:443', grpc.ssl_channel_credentials())
        self.stub = WebAccountApiStub(self.channel)
        
        # Актуальные сессионные данные
        self.session_data = {
            'sessionKey': '3PC1KLGOjzQZwHMdbwfCdU',
            'sessionId': '5P2qfQVZcRGMldmHzyfAaI',
            'device-type': 'ios',
            'x-real-ip': '138.199.55.230',
            'user-agent': '{"ua": {"device": "iPhone 15 Pro", "osVersion": "18.0.1"}, "imei": "9C2F553F-06EB-42C2-AF92-5D3BBF9304E1", "deviceName": "", "deviceType": "ios", "macAddress": "9C2F553F-06EB-42C2-AF92-5D3BBF9304E1"}',
            'user-agent-c': '18.0.1; iPhone 15 Pro',
            'app-type': 'I'
        }
        
        # Доступные endpoints
        self.endpoints = ['GET_ACCOUNTS', 'GET_LOANS', 'GET_DEPOSITS']
    
    def _get_metadata(self):
        """Генерирует метадату для запроса"""
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
    
    def call_endpoint(self, endpoint):
        """Вызывает endpoint и возвращает результат"""
        request = WebAccountsRequest(code=endpoint, data=json.dumps({}))
        metadata = self._get_metadata()
        
        try:
            response = self.stub.makeWebAccount(request, metadata=metadata)
            return {
                'success': response.success,
                'data': response.data if response.success else None,
                'error': response.error.code if not response.success else None
            }
        except Exception as e:
            return {
                'success': False,
                'data': None,
                'error': str(e)
            }
    
    def call_all_endpoints(self):
        """Вызывает все endpoints и возвращает результаты"""
        results = {}
        for endpoint in self.endpoints:
            results[endpoint] = self.call_endpoint(endpoint)
        return results
    
    def close(self):
        """Закрывает соединение"""
        if hasattr(self, 'channel'):
            self.channel.close()

if __name__ == "__main__":
    client = WebAccountClient()
    try:
        # Тестируем все endpoints
        results = client.call_all_endpoints()
        
        print("=== РЕЗУЛЬТАТЫ WEBACCOUNT API ===")
        for endpoint, result in results.items():
            status = "✅" if result['success'] else "❌"
            data_len = len(result['data']) if result['data'] else 0
            print(f"{status} {endpoint}: {data_len} символов")
            
    finally:
        client.close() 