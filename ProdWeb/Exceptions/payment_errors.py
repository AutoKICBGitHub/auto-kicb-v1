class PaymentError(Exception):
    """Базовый класс для ошибок платежей"""
    def __init__(self, message, code=None, bank=None, amount=None):
        self.message = message
        self.code = code
        self.bank = bank
        self.amount = amount
        super().__init__(self.message)

class MinimalLimitError(PaymentError):
    """Ошибка минимального лимита платежа"""
    pass

class MaximalLimitError(PaymentError):
    """Ошибка максимального лимита платежа"""
    pass

class ButtonNotFoundError(PaymentError):
    """Ошибка отсутствия кнопки"""
    pass 