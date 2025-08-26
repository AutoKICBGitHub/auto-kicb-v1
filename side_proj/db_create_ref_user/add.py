import psycopg2
import concurrent.futures
import time

# Константы
RECORDS_COUNT = 100
PARALLEL_OPERATIONS = 20  # Количество параллельных операций в секунду

# Массив референсов для чередования
REFERRERS = [
    {
        'referrer_id': '301',
        'reg_ref': 'W1DPZI7JXRJMELXU94J7C7H1EG1N'
    },
    {
        'referrer_id': '3094',
        'reg_ref': 'UEUW687ZPI9783WOTA5V32XCIO5Z'
    }
]

def add_referral_data():
    connection = None
    try:
        connection = psycopg2.connect(
            user="postgres",
            password="postgres",
            host="localhost",
            port="5434",
            database="ibank"
        )
        cursor = connection.cursor()

        referral_data = [
            (32, 'XYJZ8MXST0MV6G6SI3I47PW8WGIP', '3163', '3085'),
            (33, 'XYJZ8MXST0MV6G6SI3I47PW8WGIP', '3164', '3085')
        ]

        insert_query = """
        INSERT INTO referral_payouts (
            id, reg_ref, user_id, referrer_id
        ) VALUES (%s, %s, %s, %s)
        """

        cursor.executemany(insert_query, referral_data)
        connection.commit()
        
        print(f"Успешно добавлено {len(referral_data)} записей в таблицу referral_payouts")
        return True

    except (Exception, psycopg2.Error) as error:
        print("Ошибка при работе с PostgreSQL:", error)
        if connection:
            connection.rollback()
        return False

    finally:
        if connection:
            cursor.close()
            connection.close()

def add_single_referral(reg_ref, user_id, referrer_id):
    connection = None
    try:
        connection = psycopg2.connect(
            user="postgres",
            password="postgres",
            host="localhost",
            port="5434",
            database="ibank"
        )
        cursor = connection.cursor()

        cursor.execute("SELECT COALESCE(MAX(id), 0) + 1 FROM referral_payouts")
        next_id = cursor.fetchone()[0]

        insert_query = """
        INSERT INTO referral_payouts (
            id, reg_ref, user_id, referrer_id
        ) VALUES (%s, %s, %s, %s)
        """

        cursor.execute(insert_query, (next_id, reg_ref, user_id, referrer_id))
        
        connection.commit()
        print(f"Добавлена запись с ID {next_id}")
        return True

    except (Exception, psycopg2.Error) as error:
        print("Ошибка:", error)
        if connection:
            connection.rollback()
        return False

    finally:
        if connection:
            cursor.close()
            connection.close()

def add_multiple_referrals(count=RECORDS_COUNT):
    connection = None
    try:
        connection = psycopg2.connect(
            user="postgres",
            password="postgres",
            host="localhost",
            port="5434",
            database="ibank"
        )
        cursor = connection.cursor()

        # Получаем существующие user_id из referral_payouts
        cursor.execute("SELECT user_id FROM referral_payouts")
        existing_user_ids = set(str(row[0]) for row in cursor.fetchall())

        # Получаем ID пользователей с типом 'I'
        cursor.execute("SELECT id FROM customers WHERE customer_type = 'I' LIMIT %s", (count * 2,))  # Берем с запасом
        potential_user_ids = [str(row[0]) for row in cursor.fetchall()]

        # Фильтруем только уникальные ID, которых еще нет в referral_payouts
        user_ids = [user_id for user_id in potential_user_ids if user_id not in existing_user_ids][:count]

        if not user_ids:
            print("Не найдены подходящие пользователи с типом 'I'")
            return

        print(f"Найдено {len(user_ids)} уникальных пользователей для добавления")

        # Разбиваем на батчи по PARALLEL_OPERATIONS записей
        batches = [user_ids[i:i + PARALLEL_OPERATIONS] for i in range(0, len(user_ids), PARALLEL_OPERATIONS)]
        total_success = 0

        for batch_number, batch in enumerate(batches, 1):
            try:
                # Готовим данные для batch вставки с чередованием референсов
                batch_data = []
                records_per_referrer = len(batch) // len(REFERRERS)
                remaining_records = len(batch) % len(REFERRERS)

                current_position = 0
                for referrer in REFERRERS:
                    # Определяем количество записей для текущего референса
                    records_count = records_per_referrer
                    if remaining_records > 0:
                        records_count += 1
                        remaining_records -= 1

                    # Добавляем записи для текущего референса
                    batch_data.extend([
                        (referrer['reg_ref'], user_id, referrer['referrer_id'])
                        for user_id in batch[current_position:current_position + records_count]
                    ])
                    current_position += records_count

                # Вставляем весь batch одной командой
                cursor.executemany("""
                    INSERT INTO referral_payouts (reg_ref, user_id, referrer_id)
                    VALUES (%s, %s, %s)
                """, batch_data)

                connection.commit()
                total_success += len(batch)
                print(f"Batch {batch_number}: Добавлено {len(batch)} записей одновременно")

                # Ждем 1 секунду перед следующим батчем
                if batch_number < len(batches):
                    time.sleep(1)

            except Exception as e:
                print(f"Ошибка при добавлении batch {batch_number}: {e}")
                connection.rollback()

        print(f"Завершено добавление {total_success} записей из {len(user_ids)}")

    except (Exception, psycopg2.Error) as error:
        print("Ошибка при получении ID пользователей:", error)

    finally:
        if connection:
            cursor.close()
            connection.close()

if __name__ == "__main__":
    add_multiple_referrals()


