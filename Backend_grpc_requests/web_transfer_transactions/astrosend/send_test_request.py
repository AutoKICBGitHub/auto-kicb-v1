#!/usr/bin/env python
# -*- coding: utf-8 -*-

import grpc
import json
import argparse
from google.protobuf.json_format import ParseDict
import uuid
import time

import astrasend_internal_api_pb2 as pb2
import astrasend_internal_api_pb2_grpc as pb2_grpc

def create_request_from_json(json_data):
    """Создает объект запроса из JSON данных"""
    # Не будем изменять формат данных, так как у вас уже есть рабочий JSON
    request = pb2.ReceiveMoneyPayRequest()
    ParseDict(json_data, request)
    return request

def generate_ref_id():
    """Генерирует уникальный refid для запроса"""
    # Создаем уникальный идентификатор на основе времени и случайного UUID
    timestamp = int(time.time())
    random_uuid = str(uuid.uuid4()).replace('-', '')[:12]
    return f"REF{timestamp}{random_uuid}"

def send_receive_money_pay_request(json_data, host="localhost", port=5434):
    """Отправляет запрос receiveMoneyPay на указанный хост и порт"""
    target = f"{host}:{port}"
    
    # Создаем незащищенный канал
    channel = grpc.insecure_channel(target)
    
    # Создаем клиент
    stub = pb2_grpc.AstrasendInternalApiStub(channel)
    
    # Создаем запрос из JSON данных
    request = create_request_from_json(json_data)
    
    # Подробное логирование запроса
    print("\n=== ДЕТАЛИ ЗАПРОСА ===")
    print(f"Хост: {host}, Порт: {port}")
    
    # Логируем все поля запроса
    print("\nПОЛЯ ЗАПРОСА:")
    
    # receiverName
    if hasattr(request, 'receiverName'):
        name = request.receiverName
        print(f"receiverName: firstName={name.firstName}, middleName={name.middleName}, lastName={name.lastName}")
    
    # receiverPassport
    if hasattr(request, 'receiverPassport'):
        passport = request.receiverPassport
        print(f"receiverPassport: type={passport.type}, number={passport.number}, "
              f"issueDate={passport.issueDate}, countryOfIssue={passport.countryOfIssue}, "
              f"expiredDate={passport.expiredDate}, isExpired={passport.isExpired}")
    
    # receiverAddress
    if hasattr(request, 'receiverAddress'):
        address = request.receiverAddress
        print(f"receiverAddress: addrLine1={address.addrLine1}, city={address.city}, country={address.country}")
    
    # Другие поля
    print(f"receiverBirthDate: {request.receiverBirthDate}")
    print(f"receiverBirthPlace: {request.receiverBirthPlace}")
    print(f"marketingFlag: {request.marketingFlag}")
    print(f"receiverEmail: {request.receiverEmail}")
    print(f"receiverPhoneNumber: {request.receiverPhoneNumber}")
    print(f"receiverAccountNo: {request.receiverAccountNo}")
    
    # originatingCountryCurrency
    if hasattr(request, 'originatingCountryCurrency'):
        occ = request.originatingCountryCurrency
        print(f"originatingCountryCurrency: countryCode={occ.countryCode}, currencyCode={occ.currencyCode}")
    
    print(f"originatingCity: {request.originatingCity}")
    print(f"fixOnSend: {request.fixOnSend}")
    print(f"exchangeRate: {request.exchangeRate}")
    
    # destinationCountryCurrency
    if hasattr(request, 'destinationCountryCurrency'):
        dcc = request.destinationCountryCurrency
        print(f"destinationCountryCurrency: countryCode={dcc.countryCode}, currencyCode={dcc.currencyCode}")
    
    # originalDestinationCountryCurrency
    if hasattr(request, 'originalDestinationCountryCurrency'):
        odcc = request.originalDestinationCountryCurrency
        print(f"originalDestinationCountryCurrency: countryCode={odcc.countryCode}, currencyCode={odcc.currencyCode}")
    
    # financials
    if hasattr(request, 'financials'):
        fin = request.financials
        print(f"financials: originatorsPrincipalAmount={fin.originatorsPrincipalAmount}, "
              f"destinationPrincipalAmount={fin.destinationPrincipalAmount}, "
              f"payAmount={fin.payAmount}")
    
    print(f"mtcn: {request.mtcn}")
    print(f"newMtcn: {request.newMtcn}")
    print(f"kicbRefNo: {request.kicbRefNo}")
    print(f"isPersonalDataConfirmed: {request.isPersonalDataConfirmed}")
    
    # Генерируем уникальный refId
    ref_id = generate_ref_id()
    
    # Создаем метаданные с refid (в нижнем регистре для gRPC)
    metadata = [('refid', ref_id)]
    print(f"\nМЕТАДАННЫЕ: {metadata}")
    
    print("\n=== ОТПРАВКА ЗАПРОСА ===")
    print(f"Отправка запроса с refId: {ref_id}")
    
    try:
        # Отправляем запрос с метаданными
        response = stub.receiveMoneyPay(request, metadata=metadata)
        print("\n=== ОТВЕТ ПОЛУЧЕН ===")
        print(f"Успех: {response.success}")
        if response.success:
            print(f"MTCN: {response.data.mtcn}")
            print(f"Новый MTCN: {response.data.newMtcn}")
            print(f"Дата оплаты: {response.data.paidDate}")
            print(f"Время оплаты: {response.data.paidTime}")
            print(f"Дата расчета: {response.data.settlementDate}")
            print("Финансовые данные:")
            print(f"  Сумма отправителя: {response.data.financials.originatorsPrincipalAmount}")
            print(f"  Сумма получателя: {response.data.financials.destinationPrincipalAmount}")
            print(f"  Сумма к выплате: {response.data.financials.payAmount}")
            print(f"  Комиссия агента: {response.data.financials.agentFee}")
        else:
            print(f"Ошибка: {response.error.code}")
            print(f"Данные ошибки: {response.error.data}")
        return response
    except grpc.RpcError as e:
        print(f"\n=== ОШИБКА RPC ===")
        print(f"Код ошибки: {e.code()}")
        print(f"Детали: {e.details()}")
    finally:
        channel.close()

def main():
    parser = argparse.ArgumentParser(description='Отправка тестовых запросов к AstrasendInternalApi')
    parser.add_argument('--host', default='localhost', help='Хост сервера (по умолчанию: localhost)')
    parser.add_argument('--port', type=int, default=5434, help='Порт сервера (по умолчанию: 5434)')
    parser.add_argument('--json', help='JSON строка с данными запроса')
    parser.add_argument('--file', help='Путь к файлу с JSON данными')
    
    args = parser.parse_args()
    
    # Получаем JSON данные
    if args.json:
        json_data = json.loads(args.json)
    elif args.file:
        with open(args.file, 'r', encoding='utf-8') as f:
            json_data = json.load(f)
    else:
        # Используем данные по умолчанию из примера
        json_data = {
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
                "isExpired": True
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
    
    # Отправляем запрос
    send_receive_money_pay_request(json_data, args.host, args.port)

if __name__ == "__main__":
    main() 