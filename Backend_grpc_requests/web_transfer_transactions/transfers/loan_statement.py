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

def make_loan_statement_request(request, metadata):
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

def create_loan_statement_request():
    metadata = (
        ('refid', str(uuid.uuid1())),
        ('sessionkey', get_session_data()['session_key']),
        ('device-type', 'ios'),
        ('user-agent-c', '12; iPhone12MaxProDan'),
    )
    
    operation_id = str(uuid.uuid4())
    loan_statement_data = {
        "operationId": operation_id,
        "productType": "makeLoanStatementRequest",
        "data": {
            "statementLanguage": "ru",
            "statementRequestFee": None,
            "deliveryType": "bank",
            "deliveryFee": None,
            "deliveryAddress": None,
            "phoneNumber": "+996555599256",
            "branchCode": "001",
            "accountDebitId": 10954,
            "accountDebitIds": None,
            "loanStatementType": {
                "kg": "Ипотекалык кредитти төлөө боюнча маалымкат",
                "ru": "Справка о выплатах по ипотечному кредиту",
                "eng": "Certificate of mortgage loan repayment",
                "default": "Справка о выплатах по ипотечному кредиту",
                "operationCategoryName": None
            },
            "productType": "makeLoanStatementRequest",
            "requestId": f"IB{int(time.time() * 1000)}",
            "accountIdDebit": 10954,
            "operationId": operation_id,
            "txnId": None
        },
        "txnId": None
    }

    request = webTransferApi_pb2.IncomingWebTransfer(
        code="MAKE_TXN_SHOP_OPERATION",
        data=json.dumps(loan_statement_data)
    )
    
    response = make_loan_statement_request(request, metadata)
    print("Создание запроса справки о выплатах завершено")
    return response, loan_statement_data

def confirm_loan_statement_request(operation_id: str):
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

    response = make_loan_statement_request(request, metadata)
    print("Подтверждение запроса справки о выплатах завершено")
    return response

def execute_loan_statement_request():
    print("\n=== Начало создания запроса справки о выплатах ===")
    
    # Создаем запрос справки
    loan_statement_response, loan_statement_data = create_loan_statement_request()
    print(f"\nРезультат создания запроса: {loan_statement_response}")
    
    # Ждем 3 секунды
    print("\nОжидание 3 секунд...")
    time.sleep(3)
    
    # Подтверждаем запрос
    confirm_response = confirm_loan_statement_request(loan_statement_data["operationId"])
    print(f"\nРезультат подтверждения: {confirm_response}")
    
    return {
        "loan_statement_response": loan_statement_response,
        "confirm_response": confirm_response
    }

if __name__ == "__main__":
    try:
        result = execute_loan_statement_request()
        print("\n=== Результат выполнения ===")
        print(result)
    except Exception as e:
        print(f"\nОшибка: {str(e)}") 