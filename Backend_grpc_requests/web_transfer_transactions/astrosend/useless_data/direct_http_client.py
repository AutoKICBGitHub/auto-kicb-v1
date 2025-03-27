import requests
import json
import uuid
import time

def generate_refid():
    """Генерирует уникальный refid."""
    return str(uuid.uuid1())

def receive_money_pay(base_url, data, refid=None):
    """
    Отправляет POST-запрос для выплаты денежного перевода.
    
    Args:
        base_url: Базовый URL API
        data: Данные для запроса в формате JSON
        refid: Уникальный идентификатор запроса
    
    Returns:
        Ответ сервера
    """
    url = f"{base_url}/receive-money-pay"
    
    headers = {
        'Content-Type': 'application/json'
    }
    
    if refid:
        headers['refid'] = refid
    
    response = requests.post(url, json=data, headers=headers)
    
    try:
        return response.json()
    except:
        return {"success": False, "error": {"code": "PARSE_ERROR", "data": response.text}}

def pay_status(base_url, mtcn, new_mtcn, kicb_ref_no, refid=None):
    """
    Проверяет статус платежа.
    
    Args:
        base_url: Базовый URL API
        mtcn: Money Transfer Control Number
        new_mtcn: Новый Money Transfer Control Number
        kicb_ref_no: KICB Reference Number
        refid: Уникальный идентификатор запроса
    
    Returns:
        Ответ сервера
    """
    url = f"{base_url}/pay-status"
    
    data = {
        "mtcn": mtcn,
        "newMtcn": new_mtcn,
        "kicbRefNo": kicb_ref_no
    }
    
    headers = {
        'Content-Type': 'application/json'
    }
    
    if refid:
        headers['refid'] = refid
    
    response = requests.post(url, json=data, headers=headers)
    
    try:
        return response.json()
    except:
        return {"success": False, "error": {"code": "PARSE_ERROR", "data": response.text}}

def main():
    # Базовый URL API
    base_url = "http://localhost:5434/api/astrasend"
    
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
    
    # Отправляем запрос
    pay_result = receive_money_pay(base_url, request_data, refid)
    print("Результат выплаты:", pay_result)
    
    # Проверяем статус платежа
    status_result = pay_status(
        base_url,
        mtcn="3142256907",
        new_mtcn="090120253142256907",
        kicb_ref_no="6Da0YoXZA3K6DpnDNy3oUW",
        refid=refid
    )
    print("Статус платежа:", status_result)

if __name__ == "__main__":
    main() 