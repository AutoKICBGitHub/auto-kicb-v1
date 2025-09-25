import uuid
import grpc
import json
import time
import sys
from logger import TransferLogger
from transfer_validator import TransferValidator
sys.path.append('C:/project_kicb/Backend_grpc_requests')
import protofile_pb2 as webTransferApi_pb2
import protofile_pb2_grpc as webTransferApi_pb2_grpc

def get_transfer_data():
    with open('C:/project_kicb/side_proj/astrasend_tests/transfer_data.json', 'r', encoding='utf-8') as file:
        transfer_data = json.load(file)
    return transfer_data['data']

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
        try:
            client = webTransferApi_pb2_grpc.WebTransferApiStub(channel)
            response = client.makeWebTransfer(request, metadata=metadata)
            
            print("\nПолучен ответ:")
            response_dict = {}
            
            # Безопасно получаем все поля ответа
            for field in ['success', 'status', 'message', 'data', 'error', 'request']:
                if hasattr(response, field):
                    value = getattr(response, field)
                    response_dict[field] = value
                    if field == 'data' and value:
                        try:
                            response_dict[field] = json.loads(value)
                        except json.JSONDecodeError:
                            response_dict[field] = value
            
            # Выводим структурированный ответ
            for key, value in response_dict.items():
                if isinstance(value, (dict, list)):
                    print(f"{key.capitalize()}: {json.dumps(value, indent=2, ensure_ascii=False)}")
                else:
                    print(f"{key.capitalize()}: {value}")
            print()
            
            # Проверяем успешность ответа
            if hasattr(response, 'success') and not response.success:
                error_msg = getattr(response, 'error', '') or getattr(response, 'message', 'Неизвестная ошибка')
                raise Exception(f"Ошибка от сервера: {error_msg}")
                
            return response
            
        except grpc.RpcError as e:
            error_message = f"gRPC ошибка: {str(e)}"
            print(f"\nОшибка при отправке запроса: {error_message}")
            raise Exception(error_message)

def create_astrosend_payment():
    transfer_data = get_transfer_data()
    ref_id = str(uuid.uuid4())
    metadata = (
        ('refid', ref_id),
        ('sessionkey', transfer_data['sessionKey']),
        ('device-type', 'ios'),
        ('user-agent-c', '12; iPhone12MaxProDan'),
    )
    
    operation_id = str(uuid.uuid1())
    payment_data = {
        "operationId": operation_id,
        "accountIdDebit": transfer_data['accountIdDebit'],  # ID счета списания
        "amountCredit": "500",  # Сумма платежа
        "moneyTransferType": "ASTRASEND_OUT",  # Тип перевода
        "creditCcy": transfer_data['creditCcy'],  # Валюта
        "recipientCountryCode": "KAZ",  # Код страны получателя
        "recipientFirstName": transfer_data['recipientFirstName'],  # Имя получателя
        "recipientLastName": transfer_data['recipientLastName'],  # Фамилия получателя
        "marketingFlag": "true",  # Маркетинговый флаг
        "propValue": transfer_data['propValue']  # Значение свойства
    } 
    
    # Валидация перевода
    validator = TransferValidator()
    is_valid, error_message = validator.validate_transfer(payment_data, metadata)
    
    if not is_valid:
        raise ValueError(f"Ошибка валидации: {error_message}")

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
        ('sessionkey', get_transfer_data()['sessionKey']),
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
    logger = TransferLogger()
    print("\n=== Начало выполнения платежа Astrosend ===")
    
    try:
        # Создаем платеж
        payment_response, operation_id = create_astrosend_payment()
        print(f"\nРезультат создания платежа: {payment_response}")
        
        # Логируем создание платежа
        response_data = {}
        request_data = {}
        
        # Получаем данные запроса
        if hasattr(payment_response, 'request') and hasattr(payment_response.request, 'data'):
            try:
                request_data = json.loads(payment_response.request.data)
            except (json.JSONDecodeError, AttributeError):
                request_data = {"raw_request": str(payment_response.request)}
                
        # Получаем данные ответа
        if hasattr(payment_response, 'data'):
            try:
                response_data = json.loads(payment_response.data)
            except (json.JSONDecodeError, AttributeError):
                response_data = {"raw_response": str(payment_response)}
        
        logger.log_transfer(
            operation_id=operation_id,
            request_data=request_data,
            response_data=response_data,
            status="create"
        )
        
        # Ждем 2 секунды
        print("\nОжидание 2 секунд...")
        time.sleep(2)
        
        # Подтверждаем платеж
        confirm_response = confirm_astrosend_payment(operation_id)
        print(f"\nРезультат подтверждения: {confirm_response}")
        
        # Логируем подтверждение платежа
        confirm_response_data = {}
        if hasattr(confirm_response, 'data'):
            try:
                confirm_response_data = json.loads(confirm_response.data)
            except (json.JSONDecodeError, AttributeError):
                confirm_response_data = {"raw_response": str(confirm_response)}
        
        logger.log_transfer(
            operation_id=operation_id,
            request_data={"operationId": operation_id, "otp": "111111"},
            response_data=confirm_response_data,
            status="confirm"
        )
        
        return {
            "payment_response": payment_response,
            "confirm_response": confirm_response,
            "operation_id": operation_id
        }
        
    except Exception as e:
        # Логируем ошибку
        logger.log_transfer(
            operation_id=operation_id if 'operation_id' in locals() else str(uuid.uuid4()),
            request_data={},
            response_data={"error": str(e)},
            status="error"
        )
        raise

if __name__ == "__main__":
    try:
        result = execute_astrosend_payment()
        print("\n=== Результат выполнения ===")
        print(result)
        
        # Показываем логи для этой операции
        logger = TransferLogger()
        logs = logger.get_transfer_logs(operation_id=result["operation_id"])
        print("\n=== Логи операции ===")
        print(json.dumps(logs, indent=4, ensure_ascii=False))
        
    except Exception as e:
        print(f"\nОшибка: {str(e)}")
