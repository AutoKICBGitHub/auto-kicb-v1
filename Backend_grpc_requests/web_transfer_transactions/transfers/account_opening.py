import uuid
import grpc
import json
import time
import sys
sys.path.append('C:/project_kicb/Backend_grpc_requests')
import protofile_pb2 as webTransferApi_pb2
import protofile_pb2_grpc as webTransferApi_pb2_grpc

def get_session_data():
    with open('C:/project_kicb/Backend_grpc_requests/web_transfer_transactions/data/session_data.json', 'r') as file:
        session_data = json.load(file)
    return session_data

def make_account_opening_request(request, metadata):
    print(f"Отправка запроса: {request.code}")
    print(f"Данные запроса: {request.data}")
    print(f"Метаданные: {metadata}")
    
    with grpc.secure_channel(
            'newibanktest.kicb.net:443',
            grpc.ssl_channel_credentials(),
            options=[('grpc.enable_http_proxy', 0),
                    ('grpc.keepalive_timeout_ms', 10000)]
    ) as channel:
        client = webTransferApi_pb2_grpc.WebTransferApiStub(channel)
        response = client.makeWebTransfer(request, metadata=metadata)
        print(f"Получен ответ: {response}")
        return response

def create_account_opening_request():
    metadata = (
        ('refid', str(uuid.uuid1())),
        ('sessionkey', get_session_data()['session_key']),
        ('device-type', 'ios'),
        ('user-agent-c', '12; iPhone12MaxProDan'),
    )
    
    operation_id = str(uuid.uuid4())
    account_opening_data = {
        "operationId": operation_id,
        "productType": "makeAccountOpeningApplication",
        "data": {
            "accountDebitId": 10954,
            "openAccountCcy": "TRY",
            "productType": "makeAccountOpeningApplication",
            "requestId": f"IB{int(time.time() * 1000)}",
            "accountIdDebit": 10954,
            "operationId": operation_id,
            "txnId": None
        },
        "txnId": None
    }

    request = webTransferApi_pb2.IncomingWebTransfer(
        code="MAKE_TXN_SHOP_OPERATION",
        data=json.dumps(account_opening_data)
    )
    
    response = make_account_opening_request(request, metadata)
    print("Создание запроса на открытие счета завершено")
    return response, account_opening_data

def confirm_account_opening_request(operation_id: str):
    metadata = (
        ('refid', str(uuid.uuid1())),
        ('sessionkey', get_session_data()['session_key']),
        ('device-type', 'ios'),
        ('user-agent-c', '12; iPhone12MaxProDan'),
    )

    confirm_data = {
        "operationId": operation_id,
        "otp": "111111"
    }

    request = webTransferApi_pb2.IncomingWebTransfer(
        code="CONFIRM_TRANSFER",
        data=json.dumps(confirm_data)
    )

    response = make_account_opening_request(request, metadata)
    print("Подтверждение запроса на открытие счета завершено")
    return response

def execute_account_opening_request():
    print("\n=== Начало создания запроса на открытие счета ===")
    
    # Создаем запрос на открытие счета
    account_opening_response, account_opening_data = create_account_opening_request()
    print(f"\nРезультат создания запроса: {account_opening_response}")
    
    # Ждем 3 секунды
    print("\nОжидание 3 секунд...")
    time.sleep(2)
    
    # Подтверждаем запрос
    confirm_response = confirm_account_opening_request(account_opening_data["operationId"])
    print(f"\nРезультат подтверждения: {confirm_response}")
    
    return {
        "account_opening_response": account_opening_response,
        "confirm_response": confirm_response
    }

if __name__ == "__main__":
    try:
        result = execute_account_opening_request()
        print("\n=== Результат выполнения ===")
        print(result)
    except Exception as e:
        print(f"\nОшибка: {str(e)}") 