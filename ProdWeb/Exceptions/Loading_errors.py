class Loading_errors(Exception):
    """Класс для пользовательской ошибки."""
    def __init__(self, message, code):
        super().__init__(message)
        self.code = code