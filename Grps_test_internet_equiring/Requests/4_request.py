import sys
import os
import psycopg2
import json

# Получаем абсолютный путь к файлу txnIds.py
txnids_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'txnIds.py')

def load_txn_ids(filename):
    """Загружает ID транзакций из файла txnIds.py."""
    try:
        with open(filename, "r") as f:
            content = f.read()
            # Создаем локальное пространство имен для выполнения
            local_dict = {}
            exec(content, {}, local_dict)
            return local_dict.get('txnIds', {})
    except Exception as e:
        print(f"Ошибка при загрузке транзакций из файла {filename}: {e}")
        return {}

def get_additional_data_from_db(txn_ids):
    """Получает дополнительные данные из базы данных по ID транзакций."""
    connection = None
    records = {}
    try:
        # Подключаемся к базе данных
        connection = psycopg2.connect(
            user="postgres",
            password="postgres",
            host="localhost",
            port="5434",
            database="ibank"
        )
        cursor = connection.cursor()

        # Формируем SQL-запрос с использованием идентификаторов транзакций
        txn_ids_tuple = tuple(txn_ids.values())  # Преобразуем значения в кортеж
        query = """
            SELECT id, additional_data FROM transactions
            WHERE txn_code ILIKE %s
            AND id IN %s
            ORDER BY id DESC;
        """
        cursor.execute(query, ('%acquiring%', txn_ids_tuple))

        # Получаем данные
        db_records = cursor.fetchall()

        # Сохраняем только поле otp в словарь
        for record in db_records:
            txn_id = record[0]  # ID транзакции
            additional_data = record[1]  # Дополнительные данные

            # Предполагается, что additional_data - это JSON или словарь
            if isinstance(additional_data, str):  # Если данные в виде строки, десериализуем их
                additional_data = json.loads(additional_data)

            otp = additional_data.get("otp")  # Извлекаем только поле otp
            if otp:  # Проверяем, что otp не пустой
                records[txn_id] = otp  # Сохраняем только otp под ID транзакции

        # Проверка наличия данных
        if records:
            print("Дополнительные данные, возвращенные из базы данных:")
            for txn_id, otp in records.items():
                print(f"Txn ID: {txn_id}, OTP: {otp}")
        else:
            print("Запрос не вернул данных.")

    except (Exception, psycopg2.Error) as error:
        print(f"Ошибка при работе с PostgreSQL: {error}")

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

    return records

def save_data_to_file(records, filename):
    """Сохраняет все данные в файл в формате Python."""
    output_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), filename)
    try:
        with open(output_path, "w", encoding='utf-8') as f:
            f.write("data = {\n")
            for txn_id, otp in records.items():
                f.write(f"    '{txn_id}': '{otp}',\n")
            f.write("}\n")
        print(f"Файл {output_path} обновлён с добавлением данных.")
    except Exception as e:
        print(f"Ошибка при сохранении данных в файл {output_path}: {e}")

# Загружаем ID транзакций из файла txnIds.py
txn_ids = load_txn_ids(txnids_path)

# Получаем дополнительные данные из базы данных, используя загруженные ID
if txn_ids:
    additional_data = get_additional_data_from_db(txn_ids)
    # Сохраняем все данные в файл data.py
    save_data_to_file(additional_data, 'data.py')
else:
    print("Не найдены ID транзакций для обработки")
