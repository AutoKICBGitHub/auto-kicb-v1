import asyncio
import json
import http.client
from aiohttp import ClientSession
from faker import Faker
from Grps_test_internet_equiring.tokens import tokens  # Импортируем массив токенов
from Grps_test_internet_equiring.phone_numbers import phone_numbers  # Импортируем массив номеров телефонов

# Создаем экземпляр Faker
fake = Faker()

# Словарь для хранения txnId
txn_ids = {}


# Функция для отправки POST-запроса
async def send_request(session, token, phone_number):
    # Генерируем случайную сумму
    amount = round(fake.random_number(digits=5), 2)  # Генерируем случайную сумму (например, до 99999)

    # Создаем полезную нагрузку для запроса
    payload = json.dumps({
        "phoneNumber": phone_number,
        "amount": amount
    })

    # Указываем заголовки
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }

    # Отправляем POST-запрос
    async with session.post("https://newibanktest.kicb.net/internet-acquiring/validate",
                            headers=headers, data=payload) as response:
        data = await response.text()
        response_json = json.loads(data)  # Парсим ответ в JSON

        # Извлекаем txnId из ответа
        txn_id = response_json.get('txnId')  # Проверьте правильный ключ в ответе

        if txn_id:
            # Сохраняем txnId с наименованием txnId1, txnId2 и так далее
            txn_key = f'txnId{len(txn_ids) + 1}'
            txn_ids[txn_key] = txn_id  # Сохраняем txnId в словарь

        # Печатаем ответ сервера
        print(f"Response for token {token} and phone number {phone_number}: {data}")


# Основная асинхронная функция
async def main():
    async with ClientSession() as session:
        # Создаем список задач
        tasks = []
        for token in tokens:
            for phone_number in phone_numbers:
                task = send_request(session, token, phone_number)
                tasks.append(task)

                # Если 6 задач уже добавлены, ждем 3 секунды перед добавлением новых
                if len(tasks) >= 100:
                    await asyncio.gather(*tasks)  # Выполняем 6 запросов
                    tasks.clear()  # Очищаем список задач
                    await asyncio.sleep(1)  # Ждем 3 секунды

        # Выполняем оставшиеся запросы
        if tasks:
            await asyncio.gather(*tasks)


# Запуск программы
if __name__ == "__main__":
    asyncio.run(main())

# Сохраняем txnIds в файл
with open("../txnIds.py", "w") as f:
    f.write("txnIds = {\n")  # Открывающая фигурная скобка
    for key, value in txn_ids.items():
        f.write(f'    "{key}": "{value}",\n')  # Форматируем каждую запись
    f.write("}\n")  # Закрывающая фигурная скобка
    print("Файл txnIds.py обновлен.")
