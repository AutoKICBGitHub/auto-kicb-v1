import asyncio
import json
from aiohttp import ClientSession
from Grps_test_internet_equiring.tokens import tokens  # Импортируем массив токенов
from Grps_test_internet_equiring.new_data import data  # Импортируем словарь с данными

# Убедитесь, что у вас есть хотя бы один токен
if not tokens:
    print("Нет доступных токенов")
    exit(1)

# Словарь для хранения ответов
responses = {}

# Функция для отправки POST-запроса
async def send_request(session, transaction_id, transaction_data):
    payload = json.dumps({
        "transactionId": transaction_data['transactionId'],
        "otp": transaction_data['otp']
    })

    # Используем первый токен из массива
    headers = {
        'Authorization': f'Bearer {tokens[0]}',  # Подставляем токен
        'Content-Type': 'application/json'
    }

    # Выполняем POST-запрос
    try:
        async with session.post("https://newibanktest.kicb.net/internet-acquiring/create-transaction",
                                headers=headers, data=payload) as response:
            response_data = await response.text()

            # Сохраняем ответ в словарь
            responses[transaction_id] = response_data
            print(f"Response for transactionId {transaction_id}: {response_data}")

    except Exception as e:
        print(f"Error occurred for transactionId {transaction_id}: {str(e)}")
        responses[transaction_id] = f"Error: {str(e)}"

# Основная асинхронная функция
async def main():
    async with ClientSession() as session:
        tasks = []  # Список задач

        # Итерируемся по всем элементам data
        for i, (transaction_id, transaction_data) in enumerate(data.items()):
            task = send_request(session, transaction_id, transaction_data)
            tasks.append(task)

            # Если достигнуто 40 задач, ждем выполнения и затем задерживаемся на 1 секунду
            if (i + 1) % 40 == 0:
                await asyncio.gather(*tasks)  # Выполняем 40 запросов
                tasks.clear()  # Очищаем список задач
                await asyncio.sleep(1)  # Ждем 1 секунду

        # Выполняем оставшиеся запросы
        if tasks:
            await asyncio.gather(*tasks)

# Запуск программы
if __name__ == "__main__":
    asyncio.run(main())

# Сохраняем все данные в файл otp_input_status.py
with open('C:/project_kicb/Grps_test_internet_equiring/otp_input_status.py', 'w', encoding='utf-8') as f:
    f.write('# Сохраненные ответы\n')
    f.write('responses = ')
    f.write(json.dumps(responses, ensure_ascii=False, indent=4))

print("Ответы сохранены в файл otp_input_status.py")
