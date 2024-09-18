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
        self.response1, self.request1 = first_request.make_request(self.get_uuid(), operation_data)


        self.response2, self.request2 = second_request.make_request(self.get_uuid(), operation_data)


        # Конец времени запроса
        end_time = time.time()
        self.request_time = end_time - start_time

        # Debug prints
        print(f"Response 1: {self.response1}")
        print(f"Request 1: {self.request1}")
        print(f"Response 2: {self.response2}")
        print(f"Request 2: {self.request2}")

    def get_results(self):
        """Возвращает результаты теста."""
        return {
            'accountIdDebit': self.operation.get('accountIdDebit', 'N/A'),
            'response1': str(self.response1),  # Ensure responses are strings
            'request1': str(self.request1),  # Ensure requests are strings
            'response2': str(self.response2),  # Ensure responses are strings
            'request2': str(self.request2),  # Ensure requests are strings
            'request_time': self.request_time
        }

if __name__ == "__main__":
    results = []
    successful_operation_ids = []

    for operation in positive_customers:
        print(f"Starting test for operation: {operation.get('accountIdDebit', 'N/A')}")
        gen = Generatives(operation)
        gen.run_requests()
        results.append(gen.get_results())  # Добавляем результаты в список

        # Проверяем, содержит ли response1 успешный operationId
        response1 = gen.response1
        if response1.get('success') and 'data' in response1:
            data = json.loads(response1['data'])
            operation_id = data.get('operationId')
            if operation_id:
                successful_operation_ids.append({"operation_id": operation_id})

        print("Test completed.\n")
        print("Waiting between requests.\n")
        time.sleep(1)  # Установите интервал, если нужно
        print("End of waiting period.\n")

    # Создаем DataFrame из результатов
    df = pd.DataFrame(results)

    # Отладочные выводы перед сохранением в Excel
    print("Results DataFrame:")
    print(df.head())

    # Записываем данные в Excel
    df.to_excel('test_results.xlsx', index=False)

    print("Data saved to file test_results.xlsx")

    # Сохраняем успешные operation IDs в файл Python в указанном формате
    with open('Arrays/successful_operation_ids.py', 'w') as f:
        formatted_ids = json.dumps(successful_operation_ids, indent=4)
        f.write(f"successful_operation_ids = {formatted_ids}\n")

    print("Successful operation IDs saved to file successful_operation_ids.py")

