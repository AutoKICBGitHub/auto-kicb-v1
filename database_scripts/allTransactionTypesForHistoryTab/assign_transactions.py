import psycopg2
import json
from datetime import datetime, timedelta

def assign_transactions_to_customer(customer_id):
    connection = None
    try:
        # Загружаем шаблоны транзакций из JSON
        with open('transaction_templates.json', 'r', encoding='utf-8') as f:
            transactions_templates = json.load(f)

        # Подключаемся к базе данных
        connection = psycopg2.connect(
            user="postgres",
            password="postgres",
            host="localhost",
            port="5434",
            database="ibank"
        )
        cursor = connection.cursor()

        # Получаем время 15 минут назад
        time_15_min_ago = datetime.now() - timedelta(minutes=15)

        # Создаем транзакции для пользователя
        for template in transactions_templates:
            insert_query = """
            INSERT INTO transactions (
                txn_code,
                txn_type,
                txn_status_internal,
                txn_status_external,
                queue_step,
                is_under_processing,
                customer_id,
                amount_debit,
                amount_credit,
                account_debit_ccy,
                account_credit_ccy,
                created_at,
                description,
                merchant_name,
                payment_purpose,
                full_name_cyr_credit,
                full_name_lat_credit,
                exchange_rate,
                exchange_rate_ccy,
                transaction_type,
                connector,
                connector_provider_id,
                payment_code,
                device_type,
                additional_data
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(insert_query, (
                template['txn_code'],
                template['txn_type'],
                template['txn_status_internal'],
                template['txn_status_external'],
                template['queue_step'],
                template['is_under_processing'],
                customer_id,
                template['amount_debit'],
                template['amount_credit'],
                template['account_debit_ccy'],
                template['account_credit_ccy'],
                time_15_min_ago,
                template['description'],
                template['merchant_name'],
                template['payment_purpose'],
                template['full_name_cyr_credit'],
                template['full_name_lat_credit'],
                template['exchange_rate'],
                template['exchange_rate_ccy'],
                template['transaction_type'],
                template['connector'],
                template['connector_provider_id'],
                template['payment_code'],
                template['device_type'],
                template['additional_data']
            ))

        connection.commit()
        print(f"Транзакции успешно созданы для пользователя {customer_id}")
        return True

    except (Exception, psycopg2.Error) as error:
        print("Ошибка при работе с PostgreSQL:", error)
        return False
    except json.JSONDecodeError as error:
        print("Ошибка при чтении JSON файла:", error)
        return False
    finally:
        if connection:
            cursor.close()
            connection.close()

if __name__ == "__main__":
    customer_id = input("Введите ID пользователя: ")
    assign_transactions_to_customer(customer_id) 