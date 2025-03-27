import grpc
import json
import uuid
import time
import astrasend_internal_api_pb2 as pb2
import astrasend_internal_api_pb2_grpc as pb2_grpc
from google.protobuf.json_format import ParseDict

def generate_refid():
    """Генерирует уникальный refid."""
    return str(uuid.uuid1())

def main():
    # Адрес gRPC сервера
    server_address = "localhost:5434"
    print(f"Подключение к серверу: {server_address}")
    
    # Генерируем refid
    refid = generate_refid()
    print(f"Сгенерированный refid: {refid}")
    
    # Данные для запроса receiveMoneyPay
    request_data = {
        "receiverName": {
            "firstName": "NURLAN",
            "middleName": "BAKYNBEKOVIC",
            "lastName": "AITBAEV"
        },
        "receiverPassport": {
            "type": "A",
            "number": "ID0045377",
            "issueDate": "08062017",
            "countryOfIssue": "KGZ",
            "expiredDate": "08062027",
            "isExpired": False
        },
        "receiverAddress": {
            "addrLine1": "KG, BISHKEK 4 MKR. H.1, 43 AP.  -",
            "city": "KYRGYZSTANBISHKEK",
            "country": "KGZ"
        },
        "receiverBirthDate": "07031997",
        "receiverBirthPlace": "KGZ",
        "marketingFlag": "N",
        "receiverEmail": "fgvrs@gmail.com",
        "receiverPhoneNumber": "996708957977",
        "receiverAccountNo": "1285330001722121",
        "originatingCountryCurrency": {
            "countryCode": "UZB",
            "currencyCode": "USD"
        },
        "originatingCity": "Andizhan",
        "fixOnSend": "Y",
        "exchangeRate": 0.01027956,
        "destinationCountryCurrency": {
            "countryCode": "KGZ",
            "currencyCode": "RUB"
        },
        "originalDestinationCountryCurrency": {
            "countryCode": "KGZ",
            "currencyCode": "RUB"
        },
        "financials": {
            "originatorsPrincipalAmount": 1765,
            "destinationPrincipalAmount": 171700,
            "payAmount": 171700
        },
        "mtcn": "3142256907",
        "newMtcn": "090120253142256907",
        "kicbRefNo": "6Da0YoXZA3K6DpnDNy3oUW",
        "isPersonalDataConfirmed": True
    }
    
    print("Отправка запроса receiveMoneyPay с данными:")
    print(json.dumps(request_data, indent=2))
    
    try:
        # Создаем gRPC канал
        channel = grpc.insecure_channel(server_address)
        stub = pb2_grpc.AstrasendInternalApiStub(channel)
        
        # Создаем запрос из JSON
        request = ParseDict(request_data, pb2.ReceiveMoneyPayRequest())
        
        # Создаем метаданные с refid
        metadata = [("refid", refid)]
        
        # Отправляем запрос
        response = stub.receiveMoneyPay(request, metadata=metadata)
        
        # Обрабатываем ответ
        if response.success:
            print("Результат выплаты: Успешно")
            print(f"MTCN: {response.data.mtcn}")
            print(f"Новый MTCN: {response.data.newMtcn}")
            print(f"Дата выплаты: {response.data.paidDate}")
            print(f"Время выплаты: {response.data.paidTime}")
        else:
            print(f"Ошибка: {response.error.code}")
            print(f"Детали ошибки: {response.error.data}")
        
        # Проверяем статус платежа
        status_request = pb2.PayStatusRequest(
            mtcn="3142256907",
            newMtcn="090120253142256907",
            kicbRefNo="6Da0YoXZA3K6DpnDNy3oUW"
        )
        
        status_response = stub.payStatus(status_request, metadata=metadata)
        
        if status_response.success:
            print("Статус платежа: Успешно")
            print(f"Статус: {status_response.data.payStatusDescription}")
        else:
            print(f"Ошибка при проверке статуса: {status_response.error.code}")
            print(f"Детали ошибки: {status_response.error.data}")
        
    except Exception as e:
        print(f"Ошибка при подключении к серверу: {e}")
    finally:
        if 'channel' in locals():
            channel.close()

if __name__ == "__main__":
    main() 