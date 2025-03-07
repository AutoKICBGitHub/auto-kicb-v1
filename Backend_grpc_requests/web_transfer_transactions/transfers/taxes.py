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

def make_tax_payment(request, metadata):
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

def get_tax_codes():
    with open('C:/project_kicb/Backend_grpc_requests/web_transfer_transactions/data/taxes_codes.json', 'r', encoding='utf-8') as file:
        tax_data = json.load(file)
    return tax_data

def create_tax_payment(tax_info):
    metadata = (
        ('refid', str(uuid.uuid1())),
        ('sessionkey', get_session_data()['session_key']),
        ('device-type', 'ios'),
        ('user-agent-c', '12; iPhone12MaxProDan'),
    )
    
    # Формируем chapterCode: добавляем три нуля после кода налога
    chapter_code = f"{tax_info['taxCode']}000"
    
    tax_payment_data = {
        "operationId": str(uuid.uuid1()),
        "serviceProviderId": 923,
        "accountIdDebit": 10954,
        "amountCredit": "10",
        "tin": "23003199701323",
        "rayonCode": "003",
        "rayonName": "Свердловский р-н",
        "countrySideCode": "003",
        "countrySideName": "Свердловское УГНС",
        "taxCode": tax_info["taxCode"],
        "taxName": tax_info["text"],
        "chapterCode": "11111200",
        "chapterName": tax_info["text"],
        "paymentCode": None
    }

    try:
        request = webTransferApi_pb2.IncomingWebTransfer(
            code="MAKE_OTHER_TAX_SALYK_PAYMENT",
            data=json.dumps(tax_payment_data, ensure_ascii=False)  # Добавляем ensure_ascii=False для корректной обработки Unicode
        )
        
        print(f"\nОтправляемые данные платежа: {json.dumps(tax_payment_data, ensure_ascii=False, indent=2)}")
        
        response = make_tax_payment(request, metadata)
        print(f"Создание налогового платежа завершено для {tax_info['shortText']}")
        return response, tax_payment_data
        
    except Exception as e:
        print(f"Ошибка при создании платежа: {str(e)}")
        print(f"Данные платежа: {json.dumps(tax_payment_data, ensure_ascii=False, indent=2)}")
        raise

def confirm_tax_payment(operation_id: str):
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

    response = make_tax_payment(request, metadata)
    print("Подтверждение налогового платежа завершено")
    return response

def execute_tax_payments():
    print("\n=== Начало выполнения серии налоговых платежей ===")
    
    tax_codes = get_tax_codes()
    results = []
    
    for tax_info in tax_codes:
        retry_count = 3  # Количество попыток
        for attempt in range(retry_count):
            try:
                print(f"\n=== Обработка налога: {tax_info['shortText']} (попытка {attempt + 1}) ===")
                
                # Создаем налоговый платеж
                payment_response, payment_data = create_tax_payment(tax_info)
                print(f"\nРезультат создания платежа: {payment_response}")
                
                # Ждем 5 секунд
                print("\nОжидание 5 секунд...")
                time.sleep(2)
                
                # Подтверждаем платеж
                confirm_response = confirm_tax_payment(payment_data["operationId"])
                print(f"\nРезультат подтверждения: {confirm_response}")
                
                results.append({
                    "tax_code": tax_info["taxCode"],
                    "tax_name": tax_info["shortText"],
                    "payment_response": payment_response,
                    "confirm_response": confirm_response,
                    "status": "success"
                })
                
                break  # Выходим из цикла попыток если всё успешно
                
            except Exception as e:
                print(f"\nОшибка при обработке налога {tax_info['shortText']}: {str(e)}")
                if attempt == retry_count - 1:  # Если это была последняя попытка
                    results.append({
                        "tax_code": tax_info["taxCode"],
                        "tax_name": tax_info["shortText"],
                        "error": str(e),
                        "status": "error"
                    })
                else:
                    print(f"Повторная попытка через 10 секунд...")
                    time.sleep(10)
            
        # Дополнительная пауза между разными налогами
        time.sleep(2)
    
    return results

if __name__ == "__main__":
    try:
        results = execute_tax_payments()
        print("\n=== Итоговый результат выполнения ===")
        for result in results:
            status = "✓" if result["status"] == "success" else "✗"
            print(f"{status} {result['tax_code']} - {result['tax_name']}")
    except Exception as e:
        print(f"\nКритическая ошибка: {str(e)}")
