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

def make_moi_dom_payment(request, metadata):
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

def create_moi_dom_payment():
    metadata = (
        ('refid', str(uuid.uuid1())),
        ('sessionkey', get_session_data()['session_key']),
        ('device-type', 'ios'),
        ('user-agent-c', '12; iPhone12MaxProDan'),
    )
    
    # Создаем структуру данных для сервисов Мой Дом
    moidom_services = {
        "address": "ул. Малдыбаева д. 7 кв. 30",
        "fullname": "Умар",
        "services": [
            {"comservice": "vodokanal", "total": "594.30", "comserviceName": "БишкекВодоКанал"},
            {"comservice": "gazprom", "total": "616.98", "comserviceName": "Газпром Кыргызстан"},
            {"comservice": "teploenergo", "total": "0.00", "comserviceName": "Бишкектеплоэнерго"},
            {"comservice": "tazalyk", "total": "387.32", "comserviceName": "МП Тазалык"},
            {"comservice": "sever_electro", "total": "0.00", "comserviceName": "БиПЭС"}
        ]
    }
    
    payment_data = {
        "operationId": str(uuid.uuid1()),
        "propValue": "1337000311090988",  # Лицевой счет
        "moidomServices": moidom_services,
        "amountCredit": "1598.6",  # Общая сумма платежа
        "serviceProviderId": 740,  # ID провайдера Мой Дом
        "accountIdDebit": 8780,  # ID счета списания
        "paymentCode": "MOI_DOM"  # Код платежа
    }

    request = webTransferApi_pb2.IncomingWebTransfer(
        code="MAKE_MOI_DOM_PAYMENT",  # Код операции для Мой Дом
        data=json.dumps(payment_data)
    )
    
    response = make_moi_dom_payment(request, metadata)
    print("Создание платежа Мой Дом завершено")
    return response, payment_data

def confirm_moi_dom_payment(operation_id: str):
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

    response = make_moi_dom_payment(request, metadata)
    print("Подтверждение платежа Мой Дом завершено")
    return response

def execute_moi_dom_payment():
    print("\n=== Начало выполнения платежа Мой Дом ===")
    
    # Создаем платеж
    payment_response, payment_data = create_moi_dom_payment()
    print(f"\nРезультат создания платежа: {payment_response}")
    
    # Ждем 5 секунд
    print("\nОжидание 5 секунд...")
    time.sleep(3)
    
    # Подтверждаем платеж
    confirm_response = confirm_moi_dom_payment(payment_data["operationId"])
    print(f"\nРезультат подтверждения: {confirm_response}")
    
    return {
        "payment_response": payment_response,
        "confirm_response": confirm_response
    }

if __name__ == "__main__":
    try:
        result = execute_moi_dom_payment()
        print("\n=== Результат выполнения ===")
        print(result)
    except Exception as e:
        print(f"\nОшибка: {str(e)}")

