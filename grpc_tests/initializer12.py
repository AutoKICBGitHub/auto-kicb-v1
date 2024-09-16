import uuid
import time
import json
import pandas as pd
from grpc_tests.Arrays.operations_data import operations
from grpc_tests.Arrays.positive_customers_data import positive_customers
from grpc_tests.Arrays import successful_operation_ids

class Generatives:
    """Класс для генерации UUID и работы с массивом данных."""

    def __init__(self, positive_customers):
        """Генерация UUID при инициализации класса и сохранение операции."""
        self.uuID = str(uuid.uuid4())  # Генерация UUID
        self.operation = positive_customers   # Сохранение операции

    def get_uuid(self):
        """Возвращает ранее сгенерированный UUID."""
        return self.uuID  # Возвращаем один и тот же UUID для обоих запросов

    def get_operation_data(self):
        """Возвращает объект операции."""
        return self.operation

    def run_requests(self):
        """Запускает оба файла с запросами."""
        from grpc_tests.Requests_runs import first_request
        from grpc_tests.Requests_runs import second_request

        # Получаем данные операции
        operation_data = self.get_operation_data()

        start_time = time.time()

        # Передаем один и тот же UUID и данные операции в оба запроса
        self.response1 = first_request.make_request(self.get_uuid(), operation_data)
        self.response2 = second_request.make_request(self.get_uuid(), operation_data)

        # Конец времени запроса
        end_time = time.time()
        self.request_time = end_time - start_time

        # Debug prints
        print(f"Response 1: {self.response1}")
        print(f"Response 2: {self.response2}")

    def get_results(self):
        """Возвращает результаты теста."""
        return {
            'accountIdDebit': self.operation.get('accountIdDebit', 'N/A'),
            'response1': str(self.response1),  # Ensure responses are strings
            'response2': str(self.response2),  # Ensure responses are strings
            'request_time': self.request_time
        }

if __name__ == "__main__":
    # Список для хранения результатов
    results = []
    successful_operation_ids = []  # List to store successful operation IDs

    # Итерируемся по каждой операции в массиве и запускаем тесты
    for operation in positive_customers:
        print(f"Запуск теста для операции: {operation.get('accountIdDebit', 'N/A')}")
        gen = Generatives(operation)
        gen.run_requests()
        results.append(gen.get_results())  # Добавляем результаты в список

        # Check if response1 contains a successful operationId
        response1 = gen.response1
        if response1.get('success') and 'data' in response1:
            data = json.loads(response1['data'])
            operation_id = data.get('operationId')
            if operation_id:
                # Append the operation ID as a dictionary
                successful_operation_ids.append({"operation_id": operation_id})

        print("Тест завершен.\n")
        print("Запущенно ожидание между запросами.\n")
        time.sleep(0)  # Установите интервал, если нужно
        print("Конец ожидания между запросами.\n")

    # Создаем DataFrame из результатов
    df = pd.DataFrame(results)

    # Debug prints before saving to Excel
    print("Results DataFrame:")
    print(df.head())

    # Записываем данные в Excel
    df.to_excel('test_results.xlsx', index=False)

    print("Данные сохранены в файл test_results.xlsx")

    # Write successful operation IDs to a Python file in the specified format
    with open('Arrays/successful_operation_ids.py', 'w') as f:
        # Convert list to a JSON string with double quotes
        formatted_ids = json.dumps(successful_operation_ids, indent=4)
        f.write(f"successful_operation_ids = {formatted_ids}\n")

    print("Успешные operationId сохранены в файл successful_operation_ids.py")
