import asyncio
import json
import http.client
from aiohttp import ClientSession
from faker import Faker
from phone_numbers import phone_numbers  # Изменили импорт

# Читаем токен из JSON файла
with open('C:\\project_kicb\\Grps_test_internet_equiring\\tokens.json', 'r') as f:
    token_data = json.load(f)
    access_token = token_data['access_token']  # Берем access_token

# Создаем экземпляр Faker
fake = Faker()

# Словарь для хранения txnId
txn_ids = {}


# Функция для отправки POST-запроса
async def send_request(session, phone_number):
    payload = json.dumps({
        "phoneNumber": phone_number,
        "amount": 1
    })

    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }

    try:
        async with session.post("https://newibanktest.kicb.net/internet-acquiring/validate",
                              headers=headers, data=payload) as response:
            data = await response.text()
            print(f"\nОтвет для {phone_number}:")
            print(data)
            
            response_json = json.loads(data)
            if 'transactionId' in response_json:  # Проверяем наличие transactionId
                txn_key = f'txnId{len(txn_ids) + 1}'
                txn_ids[txn_key] = response_json['transactionId']  # Сохраняем transactionId
                
    except Exception as e:
        print(f"Ошибка для {phone_number}: {e}")


# Основная асинхронная функция
async def main():
    async with ClientSession() as session:
        tasks = []
        for phone_number in phone_numbers:
            task = send_request(session, phone_number)
            tasks.append(task)

            if len(tasks) >= 15:
                await asyncio.gather(*tasks)
                tasks.clear()
                await asyncio.sleep(1)

        if tasks:
            await asyncio.gather(*tasks)


# Запуск программы
if __name__ == "__main__":
    asyncio.run(main())

# Сохраняем txnIds в файл
txn_file_path = 'C:\\project_kicb\\Grps_test_internet_equiring\\txnIds.py'

try:
    with open(txn_file_path, "w") as f:
        f.write("txnIds = {\n")  # Открывающая фигурная скобка
        for key, value in txn_ids.items():
            f.write(f'    "{key}": "{value}",\n')  # Форматируем каждую запись
        f.write("}\n")  # Закрывающая фигурная скобка
        print(f"Файл {txn_file_path} обновлен.")
except Exception as e:
    print(f"Ошибка при сохранении файла: {e}")
