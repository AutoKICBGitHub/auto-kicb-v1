# test_requests.py
import pytest
import grpc
import json
import sys
import os
import uuid
from pytest_ordering import pytest  # Добавляем импорт для поддержки order

sys.path.append(os.path.abspath("C:\\project_kicb\\Backend_grpc_requests"))

from Backend_grpc_requests.grpc_fixture import integration_client, transfer_client, get_metadata
from protofile_pb2 import WebIntegrationRequest, IncomingWebTransfer

def load_tax_data():
    """Загрузка списка налогов из data.json"""
    json_file_path = 'C:\\project_kicb\\Backend_grpc_requests\\data.json'
    with open(json_file_path, 'r', encoding='utf-8') as json_file:
        data = json.load(json_file)
        return data.get("tax_types", [])

def update_data_json(response):
    """Обновление файла data.json на основе полученного ответа"""
    json_file_path = 'C:\\project_kicb\\Backend_grpc_requests\\data.json'
    try:
        # Читаем текущие данные
        with open(json_file_path, 'r', encoding='utf-8') as json_file:
            data = json.load(json_file)
        
        if not hasattr(response, 'data') or not response.data:
            print("Нет данных для обновления в ответе")
            return
            
        try:
            response_data = json.loads(response.data)
            
            # Обработка в зависимости от кода ответа
            if response.code == "GET_TAX_PAYER_BY_INN":
                # Обновляем данные налогоплательщика
                data.update({
                    "tin": response_data.get("tin"),
                    "name": response_data.get("name"),
                    "codeSts": response_data.get("codeSts")
                })
            
            elif response.code == "GET_TAX_PAYER_COUNTRY_SIDE":
                if isinstance(response_data, list) and response_data:
                    country_side = response_data[0]
                    data["countrySide"] = {
                        "id": country_side.get("codeSts"),
                        "displayText": country_side.get("name")
                    }
            
            elif response.code == "GET_TAX_PAYER_TAX_TYPES":
                if isinstance(response_data, list):
                    data["tax_types"] = response_data
            
            elif response.code == "GET_TAX_PAYER_BUDGET_CLASSIFICATION":
                if isinstance(response_data, list):
                    data["budget_classification"] = response_data
            
            elif isinstance(response_data, dict):
                # Для других типов ответов, которые являются словарями
                data.update(response_data)
            
            # Записываем обновленные данные
            with open(json_file_path, 'w', encoding='utf-8') as json_file:
                json.dump(data, json_file, ensure_ascii=False, indent=4)
            
            print(f"Данные успешно обновлены в data.json")
            print(f"Тип ответа: {response.code}")
            print(f"Количество записей: {len(response_data) if isinstance(response_data, list) else 1}")
            
        except json.JSONDecodeError as e:
            print(f"Ошибка при разборе JSON из ответа: {e}")
            print(f"Содержимое ответа: {response.data}")
            
    except Exception as e:
        print(f"Ошибка при обновлении data.json: {e}")

    print(f"\nОбновление data.json")
    print(f"Тип ответа: {type(response)}")
    print(f"Код ответа: {response.code if hasattr(response, 'code') else 'Нет кода'}")
    print(f"Данные ответа: {response.data if hasattr(response, 'data') else 'Нет данных'}")

@pytest.mark.order(1)
def test_GET_TAX_PAYER_BY_INN():
    metadata = get_metadata()
    request = WebIntegrationRequest(
        code="GET_TAX_PAYER_BY_INN",
        data=json.dumps({"tin": "10503198600628"})
    )
    try:
        response = integration_client.makeWebIntegration(request, metadata=metadata)
        print('Получен ответ от service: ', response)
        assert response is not None  # Убедитесь, что ответ не пустой
        update_data_json(response)  # Обновляем data.json с полученными данными
    except grpc.RpcError as e:
        pytest.fail(f'Ошибка от service: {e}')

@pytest.mark.order(2)
def test_GET_TAX_PAYER_RAYONS():
    metadata = get_metadata()
    request = WebIntegrationRequest(
        code="GET_TAX_PAYER_RAYONS",
        data=json.dumps({"tin": '10503198600628'})
    )
    try:
        response = integration_client.makeWebIntegration(request, metadata=metadata)
        print('Получен ответ от service: ', response)
        assert response is not None
        update_data_json(response)
    except grpc.RpcError as e:
        pytest.fail(f'Ошибка от service: {e}')

@pytest.mark.order(3)
def test_GET_TAX_PAYER_COUNTRY_SIDE():
    metadata = get_metadata()
    request = WebIntegrationRequest(
        code="GET_TAX_PAYER_COUNTRY_SIDE",
        data=json.dumps({"rayonCode": "001"})  # Используем код района
    )
    try:
        response = integration_client.makeWebIntegration(request, metadata=metadata)
        print('Получен ответ от service: ', response)
        assert response is not None
        update_data_json(response)  # Обновляем data.json с полученными данными
    except grpc.RpcError as e:
        pytest.fail(f'Ошибка от service: {e}')

@pytest.mark.order(4)
def test_GET_TAX_PAYER_BUDGET_CLASSIFICATION():
    metadata = get_metadata()
    request = WebIntegrationRequest(
        code="GET_TAX_PAYER_BUDGET_CLASSIFICATION",
        data=json.dumps({
            "tin": "10503198600628",  # Используем тот же ИНН
            "taxCode": "2080"  # Указываем конкретный код налога
        })
    )
    try:
        response = integration_client.makeWebIntegration(request, metadata=metadata)
        print('Получен ответ от service: ', response)
        assert response is not None
        update_data_json(response)  # Обновляем data.json с полученными данными
    except grpc.RpcError as e:
        pytest.fail(f'Ошибка от service: {e}')

@pytest.mark.order(5)
def test_GET_TAX_PAYER_TAX_TYPES():
    metadata = get_metadata()
    request = WebIntegrationRequest(
        code="GET_TAX_PAYER_TAX_TYPES",
        data=json.dumps({})
    )
    try:
        response = integration_client.makeWebIntegration(request, metadata=metadata)
        print('Получен ответ от service: ', response)
        assert response is not None  # Убедитесь, что ответ не пустой
        update_data_json(response)  # Обновляем data.json с полученными данными
    except grpc.RpcError as e:
        pytest.fail(f'Ошибка от service: {e}')

@pytest.mark.order(6)
@pytest.mark.parametrize('tax_type', load_tax_data())
def test_make_other_tax_salyk_payment(tax_type):
    metadata = get_metadata()
    
    print(f"\n{'='*50}")
    print(f"Тестирование оплаты налога: {tax_type['shortText']}")
    operation_id = str(uuid.uuid4())
    
    # Загружаем данные для платежа
    json_file_path = 'C:\\project_kicb\\Backend_grpc_requests\\data.json'
    with open(json_file_path, 'r', encoding='utf-8') as json_file:
        data = json.load(json_file)
    
    # Проверяем наличие необходимых данных
    if "tin" not in data:
        # Если ИНН нет в data.json, используем дефолтный
        data["tin"] = "10503198600628"
        print("Используется дефолтный ИНН:", data["tin"])
    
    if "codeSts" not in data or "name" not in data:
        # Получаем данные налогоплательщика
        taxpayer_response = test_GET_TAX_PAYER_BY_INN()
        if taxpayer_response:
            update_data_json(taxpayer_response)
            # Перечитываем обновленные данные
            with open(json_file_path, 'r', encoding='utf-8') as json_file:
                data = json.load(json_file)
    
    # Сначала получаем бюджетную классификацию для текущего налога
    budget_request = WebIntegrationRequest(
        code="GET_TAX_PAYER_BUDGET_CLASSIFICATION",
        data=json.dumps({
            "tin": data["tin"],  # Используем ИНН из data.json
            "taxCode": tax_type["taxCode"]
        })
    )
    
    try:
        budget_response = integration_client.makeWebIntegration(budget_request, metadata=metadata)
        if hasattr(budget_response, 'data') and budget_response.data:
            budget_data = json.loads(budget_response.data)
            if isinstance(budget_data, list) and len(budget_data) > 0:
                budget_item = budget_data[0]
                chapter_code = budget_item.get("chapterCode")
                chapter_name = budget_item.get("chapterName")
            else:
                print(f"Получены данные бюджетной классификации: {budget_data}")
                pytest.fail("Не получены данные бюджетной классификации в нужном формате")
        else:
            pytest.fail("Не получены данные бюджетной классификации")
    except grpc.RpcError as e:
        pytest.fail(f'Ошибка получения бюджетной классификации: {e}')
    
    # Формируем данные платежа
    payment_data = {
        "operationId": operation_id,
        "serviceProviderId": 923,
        "accountIdDebit": 8641,
        "amountCredit": 1,
        "tin": data["tin"],  # Используем ИНН из data.json
        "rayonCode": data.get("codeSts", "001"),
        "rayonName": data.get("name", ""),
        "countrySideCode": data.get("codeSts", "001"),
        "countrySideName": data.get("name", ""),
        "taxCode": tax_type["taxCode"],
        "taxName": tax_type["text"],
        "chapterCode": chapter_code,
        "chapterName": chapter_name
    }
    
    print("\nОтправляемые данные платежа:")
    print(json.dumps(payment_data, indent=2, ensure_ascii=False))
    
    request = IncomingWebTransfer(
        code="MAKE_OTHER_TAX_SALYK_PAYMENT",
        data=json.dumps(payment_data)
    )
    
    try:
        # Выполняем платеж
        payment_response = transfer_client.makeWebTransfer(request, metadata=metadata)
        print(f'\nПолучен ответ от сервера:')
        print(f'Success: {payment_response.success if hasattr(payment_response, "success") else "N/A"}')
        print(f'Data: {payment_response.data if hasattr(payment_response, "data") else "N/A"}')
        print(f'Error: {payment_response.error if hasattr(payment_response, "error") else "N/A"}')
        
        assert payment_response is not None
        
        # Если платеж успешен, подтверждаем его
        if hasattr(payment_response, 'success') and payment_response.success:
            print(f"\nПодтверждение платежа для налога {tax_type['taxCode']} с operation_id: {operation_id}")
            confirm_response = test_confirm_payment(operation_id)  # Передаем operation_id
            
            if confirm_response and hasattr(confirm_response, 'success') and confirm_response.success:
                print(f"Платеж для налога {tax_type['taxCode']} успешно подтвержден")
            else:
                print(f"Ошибка подтверждения платежа для налога {tax_type['taxCode']}")
                pytest.fail("Ошибка подтверждения платежа")
        else:
            print(f"Платеж для налога {tax_type['taxCode']} не требует подтверждения или не был успешным")
            if hasattr(payment_response, 'error'):
                pytest.fail(f"Ошибка платежа: {payment_response.error}")
        
        update_data_json(payment_response)
        
    except grpc.RpcError as e:
        print(f'Ошибка при оплате налога {tax_type["taxCode"]}: {e}')
        pytest.fail(f'Ошибка gRPC: {e}')

def test_confirm_payment(operation_id=None):
    """Подтверждение платежа с использованием operation_id"""
    metadata = get_metadata()
    
    if operation_id is None:
        pytest.fail("Не передан operation_id")
    
    request = IncomingWebTransfer(
        code="CONFIRM_PAYMENT",
        data=json.dumps({
            "operationId": operation_id,
            "otp": "111111",
        })
    )
    try:
        response = transfer_client.makeWebTransfer(request, metadata=metadata)
        print('Получен ответ подтверждения: ', response)
        assert response is not None
        update_data_json(response)
        return response
    except grpc.RpcError as e:
        print(f'Ошибка подтверждения: {e}')
        return None






