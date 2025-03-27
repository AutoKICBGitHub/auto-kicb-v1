import sys
import os
import grpc
import json
import uuid
import time

# Добавляем текущую директорию в путь поиска модулей
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

from astrasend_client import AstrasendClient

def generate_refid():
    """Генерирует уникальный refid."""
    # Используем UUID и текущее время для уникальности
    return f"KICB-{uuid.uuid4().hex[:8]}-{int(time.time())}"

def main():
    # Используем порт из SSH-туннеля
    server_address = "localhost:5434"  # Убираем параметры из URL
    print(f"Подключение к серверу через SSH-туннель: {server_address}")
    
    # Генерируем refid для всех запросов
    refid = str(uuid.uuid1())
    print(f"Сгенерированный refid: {refid}")
    
    try:
        # Создаем канал с увеличенным таймаутом
        channel = grpc.insecure_channel(
            server_address,
            options=[
                ('grpc.keepalive_time_ms', 10000),
                ('grpc.keepalive_timeout_ms', 5000),
                ('grpc.http2.max_pings_without_data', 0),
                ('grpc.keepalive_permit_without_calls', 1)
            ]
        )
        
        # Проверяем состояние канала
        try:
            grpc.channel_ready_future(channel).result(timeout=10)
            print("Успешное подключение к серверу!")
        except grpc.FutureTimeoutError:
            print("Не удалось подключиться к серверу в течение таймаута")
            return
        
        # Создаем клиент с глобальным refid
        with AstrasendClient(server_address, refid=refid) as client:
            # Используем конкретные данные для запроса receiveMoneyPay
            receiver_data = {
                "firstName": "NURLAN",
                "middleName": "BAKYNBEKOVIC",
                "lastName": "AITBAEV",
                "passportType": "A",
                "passportNumber": "ID0045377",
                "passportIssueDate": "08062017",
                "passportCountryOfIssue": "KGZ",
                "passportExpiredDate": "08062027",
                "isPassportExpired": False,
                "addrLine1": "KG, BISHKEK 4 MKR. H.1, 43 AP.  -",
                "city": "KYRGYZSTANBISHKEK",
                "country": "KGZ",
                "birthDate": "07031997",
                "birthPlace": "KGZ",
                "marketingFlag": "N",
                "email": "fgvrs@gmail.com",
                "phoneNumber": "996708957977",
                "accountNo": "1285330001722121"
            }
            
            transaction_data = {
                "mtcn": "3142256907",
                "newMtcn": "090120253142256907",
                "kicbRefNo": "6Da0YoXZA3K6DpnDNy3oUW",
                "originCountryCode": "UZB",
                "originCurrencyCode": "USD",
                "destCountryCode": "KGZ",
                "destCurrencyCode": "RUB",
                "originalDestCountryCode": "KGZ",
                "originalDestCurrencyCode": "RUB",
                "originatingCity": "Andizhan",
                "exchangeRate": 0.01027956,
                "fixOnSend": "Y",
                "originatorsPrincipalAmount": 1765,
                "destinationPrincipalAmount": 171700,
                "payAmount": 171700,
                "agentFee": 0.0,
                "isPersonalDataConfirmed": True
            }
            
            # Отправляем запрос на выплату денежного перевода
            print("Отправка запроса receiveMoneyPay с данными:")
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
            print(json.dumps(request_data, indent=2))
            
            pay_result = client.receive_money_pay(receiver_data, transaction_data)
            print("Результат выплаты:", pay_result)
            
            # Пример проверки статуса платежа
            status_result = client.pay_status(
                mtcn=transaction_data["mtcn"], 
                new_mtcn=transaction_data["newMtcn"],
                kicb_ref_no=transaction_data["kicbRefNo"]
            )
            print("Статус платежа:", status_result)
    except Exception as e:
        print(f"Ошибка при подключении к серверу: {e}")

if __name__ == "__main__":
    main() 