import uuid
import time
import pandas as pd
from grpc_tests.Arrays.operations_data import operations
from grpc_tests.Arrays.positive_customers_data import positive_customers

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
        """Возвращает результаты теста, включая успешные operationId."""
        response1_success = self.response1.get('success', False)
        response2_success = self.response2.get('success', False)

        successful_operation_ids = []

        if response1_success:
            data = self.response1.get('data', '{}')
            parsed_data = json.loads(data)
            operation_id = parsed_data.get('operationId')
            if operation_id:
                successful_operation_ids.append(operation_id)

        if response2_success:
            data = self.response2.get('data', '{}')
            parsed_data = json.loads(data)
            operation_id = parsed_data.get('operationId')
            if operation_id:
                successful_operation_ids.append(operation_id)

        return {
            'accountIdDebit': self.operation.get('accountIdDebit', 'N/A'),
            'response1': str(self.response1),  # Ensure responses are strings
            'response2': str(self.response2),  # Ensure responses are strings
            'request_time': self.request_time,
            'successful_operation_ids': ', '.join(successful_operation_ids)  # Join IDs into a string
        }

if __name__ == "__main__":
    # Список для хранения результатов
    results = []
    operation_ids = []

    # Итерируемся по каждой операции в массиве и запускаем тесты
    for operation in positive_customers:
        print(f"Запуск теста для операции: {operation.get('accountIdDebit', 'N/A')}")
        gen = Generatives(operation)
        gen.run_requests()
        result = gen.get_results()
        results.append(result)  # Добавляем результаты в список
        operation_ids.extend(result['successful_operation_ids'].split(', '))  # Добавляем успешные operationId в список
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

    # Сохраняем успешные operationId в файл
    with open('successful_operation_ids.txt', 'w') as f:
        if operation_ids:
            f.write('\n'.join(operation_ids))
        else:
            f.write("No successful operationIds found.")

    print("Данные сохранены в файл test_results.xlsx и успешные operationId в successful_operation_ids.txt")
