import uuid
import time
import json
import pandas as pd
import asyncio
from grpc_tests.Arrays.operations_data import successful_operation_ids
from grpc_tests.Arrays.positive_customers_data import positive_customers
from grpc_tests.Arrays import successful_operation_ids
from grpc_tests.Requests_runs import first_request
from grpc_tests.Requests_runs import second_request

class Generatives:
    """Класс для генерации UUID и работы с массивом данных."""

    def __init__(self, positive_customer):
        """Генерация UUID при инициализации класса и сохранение операции."""
        self.uuID = str(uuid.uuid4())  # Генерация UUID
        self.operation = positive_customer  # Сохранение операции

    def get_uuid(self):
        """Возвращает ранее сгенерированный UUID."""
        return self.uuID

    def get_operation_data(self):
        """Возвращает объект операции."""
        return self.operation

    async def run_requests(self):
        """Запускает оба файла с запросами асинхронно."""
        operation_data = self.get_operation_data()

        start_time = time.time()

        # Выполняем первый запрос
        self.response1, self.request1 = await first_request.make_request(self.get_uuid(), operation_data)

        # Ждем 4 секунды перед вторым запросом
        await asyncio.sleep(4)

        # Выполняем второй запрос
        self.response2, self.request2 = await second_request.make_request(self.get_uuid(), operation_data)

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
            'response1': str(self.response1),
            'request1': str(self.request1),
            'response2': str(self.response2),
            'request2': str(self.request2),
            'request_time': self.request_time
        }

async def main():
    results = []
    successful_operation_ids = []  # Создаем новый список для успешных ID

    semaphore = asyncio.Semaphore(9)  # Ограничение на 5 одновременных задач

    async def limited_run_requests(operation):
        async with semaphore:  # Ждем, пока можно будет запустить новую задачу
            gen = Generatives(operation)
            await gen.run_requests()
            return gen  # Возвращаем экземпляр для дальнейшей обработки

    tasks = []
    for operation in positive_customers:
        print(f"Запуск теста для операции: {operation.get('accountIdDebit', 'N/A')}")
        tasks.append(limited_run_requests(operation))

    generatives_instances = await asyncio.gather(*tasks)

    # Обработка результатов
    for gen in generatives_instances:
        results.append(gen.get_results())
        response1 = gen.response1
        if response1.get('success') and 'data' in response1:
            data = json.loads(response1['data'])
            operation_id = data.get('operationId')
            if operation_id:
                successful_operation_ids.append({"operation_id": operation_id})

    # Создаем DataFrame из результатов
    df = pd.DataFrame(results)

    # Записываем данные в Excel
    df.to_excel('test_results.xlsx', index=False)
    print("Данные сохранены в файл test_results.xlsx")

    # Сохраняем успешные operation IDs в файл Python в указанном формате
    with open('Arrays/successful_operation_ids.py', 'w') as f:
        formatted_ids = json.dumps(successful_operation_ids, indent=4)
        f.write(f"successful_operation_ids = {formatted_ids}\n")
    print("Успешные operation IDs сохранены в файл successful_operation_ids.py")

if __name__ == "__main__":
    asyncio.run(main())
