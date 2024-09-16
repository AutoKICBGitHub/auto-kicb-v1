import psycopg2
import pandas as pd
from grpc_tests.Arrays.successful_operation_ids import successful_operation_ids

def load_operation_ids():
    """Загружает operation_id из импортированного модуля."""
    try:
        # Получаем operation_id из импортированного списка
        return [entry['operation_id'] for entry in successful_operation_ids]
    except Exception as e:
        print(f"Ошибка при загрузке operation_id из модуля: {e}")
        return []

def get_transactions_from_db(operation_id):
    """Извлекает данные транзакций для конкретного operation_id из базы данных."""
    connection = None
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

        # SQL-запрос для извлечения данных транзакций по operation_id
        query = """
        SELECT txn_status_internal, txn_code, amount_debit, cbs_error_code, cbs_err_desc
        FROM transactions
        WHERE operation_id = %s;
        """

        # Выполняем запрос с параметром
        cursor.execute(query, (operation_id,))
        record = cursor.fetchone()

        # Возвращаем полный набор данных
        return record if record else None

    except (Exception, psycopg2.Error) as error:
        print("Ошибка при работе с PostgreSQL:", error)
        return None

    finally:
        if connection:
            cursor.close()
            connection.close()

def save_to_excel(data, filename):
    """Сохраняет данные в Excel файл."""
    df = pd.DataFrame(data, columns=["operation_id", "txn_status_internal", "txn_code", "amount_debit", "cbs_error_code", "cbs_err_desc"])
    df.to_excel(filename, index=False)
    print(f"Данные сохранены в файл {filename}")

# Основной блок выполнения
if __name__ == "__main__":

    # Загружаем operation_id из модуля
    operation_ids = load_operation_ids()

    if operation_ids:
        # Список для хранения данных
        transaction_data = []

        for operation_id in operation_ids:
            print(f"Запуск запроса для operation_id: {operation_id}")
            txn_data = get_transactions_from_db(operation_id)

            if txn_data is not None:
                # Добавляем operation_id и остальные данные
                transaction_data.append([operation_id] + list(txn_data))
            else:
                print(f"Нет данных для operation_id {operation_id}.")

        # Сохраняем результаты в Excel файл
        if transaction_data:
            save_to_excel(transaction_data, "transaction_data.xlsx")
        else:
            print("Нет данных для сохранения.")
    else:
        print("Нет operation_id для выполнения запросов.")
