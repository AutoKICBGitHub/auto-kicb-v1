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

def make_astrosend_payment(request, metadata):
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

def create_astrosend_payment():
    session_data = get_session_data()
    ref_id = str(uuid.uuid4())
    metadata = (
        ('refid', ref_id),
        ('sessionkey', session_data['session_key']),
        ('device-type', 'ios'),
        ('user-agent-c', '12; iPhone12MaxProDan'),
    )
    
    operation_id = str(uuid.uuid1())
    payment_data = {
        "operationId": operation_id,
        "accountIdDebit": 8641,  # ID счета списания
        "amountCredit": "500",  # Сумма платежа
        "moneyTransferType": "ASTRASEND_OUT",  # Тип перевода
        "creditCcy": "RUB",  # Валюта
        "recipientCountryCode": "KAZ",  # Код страны получателя
        "recipientFirstName": "Bularov",  # Имя получателя
        "recipientLastName": "Temirlan",  # Фамилия получателя
        "marketingFlag": "true",  # Маркетинговый флаг
        "propValue": "Акай"  # Значение свойства
    } 

    request = webTransferApi_pb2.IncomingWebTransfer(
        code="MAKE_MONEY_TRANSFER",
        data=json.dumps(payment_data)
    )
    
    response = make_astrosend_payment(request, metadata)
    print("Создание платежа Astrosend завершено")
    return response, operation_id

def confirm_astrosend_payment(operation_id: str):
    metadata = (
        ('refid', str(uuid.uuid4())),
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

    response = make_astrosend_payment(request, metadata)
    print("Подтверждение платежа Astrosend завершено")
    return response

def execute_astrosend_payment():
    print("\n=== Начало выполнения платежа Astrosend ===")
    
    # Создаем платеж
    payment_response, operation_id = create_astrosend_payment()
    print(f"\nРезультат создания платежа: {payment_response}")
    
    # Ждем 2 секунды
    print("\nОжидание 2 секунд...")
    time.sleep(2)
    
    # Подтверждаем платеж
    confirm_response = confirm_astrosend_payment(operation_id)
    print(f"\nРезультат подтверждения: {confirm_response}")
    
    return {
        "payment_response": payment_response,
        "confirm_response": confirm_response
    }

if __name__ == "__main__":
    try:
        result = execute_astrosend_payment()
        print("\n=== Результат выполнения ===")
        print(result)
    except Exception as e:
        print(f"\nОшибка: {str(e)}")
