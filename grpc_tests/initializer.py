import uuid
from grpc_tests.Arrays.operations_data import operations  # Импортируем массив операций из файла

class Generatives:
    """Класс для генерации UUID и работы с массивом данных."""

    def __init__(self, operation):
        """Генерация UUID при инициализации класса и сохранение операции."""
        self.uuID = str(uuid.uuid4())  # Генерация UUID
        self.operation = operation   # Сохранение операции

    def get_uuid(self):
        """Возвращает ранее сгенерированный UUID."""
        return self.uuID  # Возвращаем один и тот же UUID для обоих запросов

    def get_operation_data(self):
        """Возвращает объект операции."""
        return self.operation

    def run_requests(self):
        """Запускает оба файла с запросами."""
        from grpc_tests.Requests import first_request
        from grpc_tests.Requests import second_request

        # Получаем данные операции
        operation_data = self.get_operation_data()

        # Передаем один и тот же UUID и данные операции в оба запроса
        first_request.make_request(self.get_uuid(), operation_data)
        second_request.make_request(self.get_uuid(), operation_data)


if __name__ == "__main__":
    # Итерируемся по каждой операции в массиве и запускаем тесты
    for operation in operations:
        print(f"Запуск теста для операции: {operation['paymentPurpose']}")
        gen = Generatives(operation)
        gen.run_requests()
        print("Тест завершен.\n")
