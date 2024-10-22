import asyncio
import json
import aiohttp

# Загрузка txnIds из файла
txn_ids = {}
try:
    with open('C:/project_kicb/Grps_test_internet_equiring/txnIds.py', 'r', encoding='utf-8') as f:
        exec(f.read())  # Выполняем содержимое файла, чтобы получить словарь txnIds
        # Убедитесь, что переменная txnIds определена
        if 'txnIds' in locals():
            txn_ids = locals()['txnIds']  # Получаем значение txnIds
except Exception as e:
    print(f"Ошибка при загрузке txnIds: {str(e)}")

# Проверка, что txn_ids загружены
if not txn_ids:
    print("Нет доступных txnIds.")
    exit(1)

# Загрузка токенов из файла
tokens = []
with open('C:/project_kicb/Grps_test_internet_equiring/tokens.py', 'r', encoding='utf-8') as f:
    exec(f.read())  # Выполняем содержимое файла, чтобы получить список tokens

# Убедитесь, что у вас есть хотя бы один токен
if not tokens:
    print("Нет доступных токенов.")
    exit(1)

# Словарь для хранения ответов сервера
server_responses = {}

# Функция для отправки GET-запроса
async def check_transaction(session, transaction_id):
    headers = {
        'Authorization': f'Bearer {tokens[0]}',  # Используем первый токен
    }

    # Выполняем GET-запрос
    try:
        async with session.get(f"https://newibanktest.kicb.net/internet-acquiring/check-transaction/{transaction_id}", headers=headers) as response:
            # Получаем статус ответа
            status = response.status
            response_data = await response.text()
            server_responses[transaction_id] = response_data  # Сохраняем ответ в словарь

            # Отладочная информация
            print(f"Response for transactionId {transaction_id} (status: {status}): {response_data}")

            if status != 200:
                print(f"Ошибка при получении данных для transactionId {transaction_id}: {status}")

    except Exception as e:
        print(f"Ошибка произошла для transactionId {transaction_id}: {str(e)}")
        server_responses[transaction_id] = f"Error: {str(e)}"

# Основная асинхронная функция
async def main():
    async with aiohttp.ClientSession() as session:
        tasks = []

        # Итерируемся по всем txnId
        for transaction_id in txn_ids.values():
            task = check_transaction(session, transaction_id)
            tasks.append(task)

            # Если 40 задач, ждем выполнения и затем задерживаемся на 1 секунду
            if len(tasks) >= 40:
                await asyncio.gather(*tasks)  # Выполняем 40 запросов
                tasks.clear()  # Очищаем список задач
                await asyncio.sleep(1)  # Ждем 1 секунду

        # Выполняем оставшиеся запросы
        if tasks:
            await asyncio.gather(*tasks)

# Запуск программы
if __name__ == "__main__":
    asyncio.run(main())

# Сохраняем все ответы в файл server_answer.py
with open('C:/project_kicb/Grps_test_internet_equiring/server_answer.py', 'w', encoding='utf-8') as f:
    f.write('# Сохраненные ответы сервера\n')  # Комментарий перед словарем
    f.write('server_responses = {}\n')  # Инициализация пустого словаря
    f.write(json.dumps(server_responses, ensure_ascii=False, indent=4))  # Запись ответов

# Выводим ответы в консоль
print("Ответы сохранены в файл server_answer.py")
print("Полученные ответы:")
print(json.dumps(server_responses, ensure_ascii=False, indent=4))  # Выводим содержимое server_responses
