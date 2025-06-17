import grpc, json, uuid, sys, os
sys.path.append('C:\\project_kicb\\stress_tests\\memory_leak')
from protofile_pb2_grpc import WebAccountV2ApiStub
from protofile_pb2 import WebAccountsRequest

channel = grpc.secure_channel('newibanktest.kicb.net:443', grpc.ssl_channel_credentials())
v2_stub = WebAccountV2ApiStub(channel)

# Полная метадата (как у V1)
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

# Упрощенная метадата
simple_metadata = [
    ('sessionkey', '5MtEKcQbp3LZZXK5s3lNIH'),
    ('sessionid', '5P2qfQVZcRGMldmHzyfAaI'),
    ('device-type', 'ios'),
    ('refid', str(uuid.uuid4())),
    ('user-agent-c', '12; MACBOOKDANDAN')
]

print("=== ТЕСТИРОВАНИЕ РАЗНЫХ ФОРМАТОВ V2 API ===\n")

# Тестируем разные варианты data
test_cases = [
    ('Пустые данные', '{}'),
    ('accountStatus как строка', '{"accountStatus": "O"}'),
    ('Простой объект', '{"status": "O"}'),
    ('Только значение O', '"O"'),
    ('accountStatus как число', '{"accountStatus": 0}'),
    ('Другой формат', '{"account_status": "O"}'),
    ('Без JSON', 'accountStatus=O'),
]

for description, data_str in test_cases:
    print(f"🔄 {description}: {data_str}")
    
    for meta_name, metadata in [("простая", simple_metadata), ("полная", full_metadata)]:
        try:
            request = WebAccountsRequest(code='GET_ACCOUNTS', data=data_str)
            response = v2_stub.makeWebAccountV2(request, metadata=metadata)
            status = "✅" if response.success else "❌"
            error_info = f" - {response.error.code}" if not response.success else f" - {len(response.data)} символов"
            print(f"   {meta_name} метадата: {status}{error_info}")
        except Exception as e:
            print(f"   {meta_name} метадата: ❌ EXCEPTION - {e}")
    print()

channel.close() 