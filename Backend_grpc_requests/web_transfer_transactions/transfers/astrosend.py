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
    metadata = (
        ('refid', str(uuid.uuid1())),
        ('sessionkey', session_data['session_key']),
        ('device-type', 'ios'),
        ('user-agent-c', '12; iPhone12MaxProDan'),
    )
    
    payment_data = {
        "operationId": str(uuid.uuid1()),
        "propValue": "+996700000000",  # Номер телефона получателя
        "accountIdDebit": 10954,  # ID счета списания
        "amountCredit": "100",  # Сумма платежа
        "serviceId": "ASTROSEND",  # ID сервиса Astrosend
        "serviceProviderId": 937,  # ID провайдера Astrosend
        "sessionKey": session_data['session_key'],
        "refId": str(uuid.uuid1()),
        "userId": 232,
        "status": "ALLOWED",
        "sessionId": str(uuid.uuid1()),
        "customerNo": "00749190",
        "userLocale": "ru",
        "userPhoneNumber": "+996708957977",
        "userOtpDelivery": "sms",
        "lastPasswordChangeTimestamp": "Mon Mar 03 2025 13:55:33 GMT+0600 (Kyrgyzstan Time)",
        "customerIndCorp": "I",
        "username": "00749190",
        "userBranch": "001",
        "userEmail": "fgvrs@gmail.com",
        "isUserActive": True,
        "isUserReadOnly": False,
        "isCustomerReadOnly": False,
        "isJointAccount": False,
        "isTrusted": False,
        "isMaker": None,
        "isChecker": None,
        "paymentCode": "MAKE_MONEY_TRANSFER"
    } 

    request = webTransferApi_pb2.IncomingWebTransfer(
        code="MAKE_GENERIC_PAYMENT_V2",
        data=json.dumps(payment_data)
    )
    
    response = make_astrosend_payment(request, metadata)
    print("Создание платежа Astrosend завершено")
    return response, payment_data

def confirm_astrosend_payment(operation_id: str):
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

    response = make_astrosend_payment(request, metadata)
    print("Подтверждение платежа Astrosend завершено")
    return response

def execute_astrosend_payment():
    print("\n=== Начало выполнения платежа Astrosend ===")
    
    # Создаем платеж
    payment_response, payment_data = create_astrosend_payment()
    print(f"\nРезультат создания платежа: {payment_response}")
    
    # Ждем 2 секунды
    print("\nОжидание 2 секунд...")
    time.sleep(2)
    
    # Подтверждаем платеж
    confirm_response = confirm_astrosend_payment(payment_data["operationId"])
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
