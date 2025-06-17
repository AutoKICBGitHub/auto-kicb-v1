#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import grpc, json, uuid, sys, os
sys.path.append('C:\\project_kicb\\stress_tests\\memory_leak')
from protofile_pb2_grpc import WebAccountV2ApiStub
from protofile_pb2 import WebAccountsRequest

channel = grpc.secure_channel('newibanktest.kicb.net:443', grpc.ssl_channel_credentials())
v2_stub = WebAccountV2ApiStub(channel)

# Полная метадата
full_metadata = [
    ('sessionkey', '5MtEKcQbp3LZZXK5s3lNIH'), 
    ('sessionid', '5P2qfQVZcRGMldmHzyfAaI'), 
    ('device-type', 'ios'), 
    ('refid', str(uuid.uuid4())), 
    ('x-real-ip', '138.199.55.230'), 
    ('user-agent', '{"ua": {"device": "iPhone 15 Pro", "osVersion": "18.0.1"}}'), 
    ('user-agent-c', '12; MACBOOKDANDAN'), 
    ('app-type', 'I')
]

print("=== ТЕСТИРОВАНИЕ STORIES API V2 ===\n")

# Пробуем разные варианты Stories API
test_cases = [
    ('GET_LIST_OF_STORIES', '{}'),
    ('GET_LIST_OF_STORIES', '{"status": "ACTIVE"}'),
    ('GET_LIST_OF_STORIES', '{"type": "NEWS"}'), 
    ('GET_LIST_OF_STORIES', '{"limit": 10}'),
    ('GET_STORIES', '{}'),
    ('STORIES', '{}'),
    ('LIST_STORIES', '{}'),
]

for endpoint, data_str in test_cases:
    print(f"🔄 {endpoint}: {data_str}")
    try:
        request = WebAccountsRequest(code=endpoint, data=data_str)
        response = v2_stub.makeWebAccountV2(request, metadata=full_metadata)
        status = "✅" if response.success else "❌"
        if response.success:
            info = f" - {len(response.data)} символов"
            print(f"   {status}{info}")
            print(f"   📊 Первые 150 символов: {response.data[:150]}...")
        else:
            info = f" - {response.error.code}"
            print(f"   {status}{info}")
    except Exception as e:
        print(f"   ❌ EXCEPTION - {e}")
    print()

channel.close() 