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

def make_own_transfer(request, metadata):
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

def create_own_transfer():
    metadata = (
        ('refid', str(uuid.uuid1())),
        ('sessionkey', get_session_data()['session_key']),
        ('device-type', 'ios'),
        ('user-agent-c', '12; iPhone12MaxProDan'),
    )
    
    transfer_data = {
        "operationId": str(uuid.uuid1()),
        "accountIdDebit": 14657,  # Счет списания
        "accountIdCredit": 14656,  # Счет зачисления
        "amountDebit": "1",  # Сумма перевода
        # "valueDate": None,
        # "exchangeDealId": None,
        # "valueTime": None,
        # "theirRefNo": None,
        # "knp": None,
        # "paymentPurpose": None,
        # "txnId": None
    }

    request = webTransferApi_pb2.IncomingWebTransfer(
        code="MAKE_OWN_ACCOUNTS_TRANSFER",  # Код операции для перевода между своими счетами
        data=json.dumps(transfer_data)
    )
    
    response = make_own_transfer(request, metadata)
    print("Создание перевода между своими счетами завершено")
    return response, transfer_data

def confirm_own_transfer(operation_id: str):
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
        code="CONFIRM_TRANSFER",  # Код операции для подтверждения
        data=json.dumps(confirm_data)
    )

    response = make_own_transfer(request, metadata)
    print("Подтверждение перевода завершено")
    return response

def execute_own_transfer():
    print("\n=== Начало выполнения перевода между своими счетами ===")
    
    # Создаем перевод
    transfer_response, transfer_data = create_own_transfer()
    print(f"\nРезультат создания перевода: {transfer_response}")
    
    # Ждем 5 секунд
    print("\nОжидание 5 секунд...")
    time.sleep(5)
    
    # Подтверждаем перевод
    confirm_response = confirm_own_transfer(transfer_data["operationId"])
    print(f"\nРезультат подтверждения: {confirm_response}")
    
    return {
        "transfer_response": transfer_response,
        "confirm_response": confirm_response
    }

if __name__ == "__main__":
    try:
        result = execute_own_transfer()
        print("\n=== Результат выполнения ===")
        print(result)
    except Exception as e:
        print(f"\nОшибка: {str(e)}")
