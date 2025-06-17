import grpc, json, uuid, sys, os
sys.path.append('C:\\project_kicb\\stress_tests\\memory_leak')
from protofile_pb2_grpc import WebAccountV2ApiStub
from protofile_pb2 import WebAccountV2ApiRequest

channel = grpc.secure_channel('newibanktest.kicb.net:443', grpc.ssl_channel_credentials())
v1_stub = WebAccountApiStub(channel)
v2_stub = WebAccountV2ApiStub(channel)

metadata = [('sessionkey', '5MtEKcQbp3LZZXK5s3lNIH'), ('sessionid', '5P2qfQVZcRGMldmHzyfAaI'), ('device-type', 'ios'), ('refid', str(uuid.uuid4())), ('x-real-ip', '138.199.55.230'), ('user-agent', '{"ua": {"device": "iPhone 15 Pro", "osVersion": "18.0.1"}}'), ('user-agent-c', '12; MACBOOKDANDAN'), ('app-type', 'I')]

request_v1 = WebAccountsRequest(code='GET_ACCOUNTS', data='{}')  # V1 с пустыми данными
request_v2 = WebAccountsRequest(code='GET_ACCOUNTS', data='{"accountStatus": "O"}')  # V2 с параметром

print("=== GET_ACCOUNTS ТЕСТ ===")
print("🔄 Тестирую с разными форматами данных...")

print("\n1️⃣ V1 API (старый формат - пустые данные):")
try:
    response_v1 = v1_stub.makeWebAccount(request_v1, metadata=metadata)
    print(f'   ✅ V1: success={response_v1.success}, data_len={len(response_v1.data) if response_v1.data else 0}, error={response_v1.error.code if not response_v1.success else None}')
except Exception as e:
    print(f'   ❌ V1 ERROR: {e}')

print("\n2️⃣ V2 API (новый формат - с accountStatus):")
try:
    response_v2 = v2_stub.makeWebAccountV2(request_v2, metadata=metadata)
    print(f'   🎯 V2: success={response_v2.success}, data_len={len(response_v2.data) if response_v2.data else 0}, error={response_v2.error.code if not response_v2.success else None}')
    if response_v2.success and response_v2.data:
        print(f'   📊 Первые 200 символов ответа: {response_v2.data[:200]}...')
except Exception as e:
    print(f'   ❌ V2 ERROR: {e}')

print("\n3️⃣ V2 API с закрытыми счетами (accountStatus=C):")
try:
    request_v2_closed = WebAccountsRequest(code='GET_ACCOUNTS', data='{"accountStatus": "C"}')
    response_v2_closed = v2_stub.makeWebAccountV2(request_v2_closed, metadata=metadata)
    print(f'   🔒 V2 (закрытые): success={response_v2_closed.success}, data_len={len(response_v2_closed.data) if response_v2_closed.data else 0}, error={response_v2_closed.error.code if not response_v2_closed.success else None}')
except Exception as e:
    print(f'   ❌ V2 (закрытые) ERROR: {e}')

channel.close() 