import json
from typing import Dict, Tuple, Optional

class TransferValidator:
    def __init__(self):
        self.errors = []

    def validate_device_info(self, metadata: tuple) -> bool:
        """
        Проверка заполнения тегов device type/channel/bank name
        """
        device_type = next((value for key, value in metadata if key == 'device-type'), None)
        if not device_type or device_type not in ['ios', 'android', 'web']:
            self.errors.append("Некорректный device-type")
            return False
        return True

    def validate_payment_details(self, payment_data: Dict) -> bool:
        """
        Проверка направления запроса с указанием суммы выплаты в валюте выплаты
        Проверка корректности payment_type, delivery_service_code, флага fix_on_send
        """
        required_fields = {
            "amountCredit": "Сумма перевода",
            "creditCcy": "Валюта перевода",
            "moneyTransferType": "Тип перевода",
        }
        
        for field, description in required_fields.items():
            if field not in payment_data or not payment_data[field]:
                self.errors.append(f"Отсутствует {description}")
                return False

        # Проверка типа перевода
        if payment_data["moneyTransferType"] != "ASTRASEND_OUT":
            self.errors.append("Некорректный тип перевода")
            return False

        return True

    def validate_country_transfer(self, payment_data: Dict, country_code: str, currency: str) -> bool:
        """
        Проверка возможности отправки перевода в конкретную страну в конкретной валюте
        """
        if payment_data.get("recipientCountryCode") != country_code:
            self.errors.append(f"Страна получателя должна быть {country_code}")
            return False
            
        if payment_data.get("creditCcy") != currency:
            self.errors.append(f"Валюта перевода должна быть {currency}")
            return False
            
        return True

    def validate_identifiers(self, request_data: Dict) -> bool:
        """
        Проверка блока идентификаторов в запросе комиссии:
        - foreign_remote_system
        - identifier
        - reference_no
        - location_id
        - counter_id
        """
        if not request_data.get("operationId"):
            self.errors.append("Отсутствует operationId")
            return False
            
        if len(request_data["operationId"]) < 16:
            self.errors.append("operationId должен быть не менее 16 символов")
            return False
            
        return True

    def validate_transfer(self, payment_data: Dict, metadata: tuple) -> Tuple[bool, Optional[str]]:
        """
        Выполняет все проверки для перевода
        
        Returns:
            Tuple[bool, Optional[str]]: (успех валидации, сообщение об ошибке)
        """
        self.errors = []  # Сбрасываем ошибки перед проверкой
        
        validations = [
            self.validate_device_info(metadata),
            self.validate_payment_details(payment_data),
            self.validate_identifiers(payment_data)
        ]
        
        # Проверяем специфичные условия для разных стран
        if payment_data.get("recipientCountryCode") == "UZB":
            validations.append(self.validate_country_transfer(payment_data, "UZB", "USD"))
        elif payment_data.get("recipientCountryCode") == "KAZ":
            validations.append(self.validate_country_transfer(payment_data, "KAZ", "RUB"))
        elif payment_data.get("recipientCountryCode") == "TJK":
            validations.append(self.validate_country_transfer(payment_data, "TJK", "RUB"))
            
        is_valid = all(validations)
        error_message = "; ".join(self.errors) if self.errors else None
        
        return is_valid, error_message
