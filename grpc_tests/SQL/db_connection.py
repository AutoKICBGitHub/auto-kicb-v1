import psycopg2
import grpc_tests.Arrays.positive_customers_data


def get_operations_from_db():
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

        # SQL-запрос для получения всех пользователей с активными сессионными ключами
        query = """
        SELECT u.id, s.session_key, c.customer_category, c.customer_type,
               a.id as accountId, a.account_no, a.ccy, a.branch_code, a.acy_withdrawable_bal
        FROM users u
        INNER JOIN customers c ON c.customer_no = u.customer_no
        INNER JOIN accounts a ON a.customer_no = c.customer_no
        INNER JOIN (
            SELECT DISTINCT ON (user_id) *
            FROM sessions
            WHERE is_valid = true AND session_key_type = 'PERMANENT_SESSION_KEY'
            ORDER BY user_id DESC
        ) s ON s.user_id = u.id
        WHERE (u.joint_user_data IS NULL OR u.corp_user_data IS NULL)
          AND a.acy_withdrawable_bal > 0;
        """

        # Выполняем запрос
        cursor.execute(query)
        records = cursor.fetchall()

        # Вывод данных
        if records:
            print("Данные, возвращенные из базы данных:")
            for record in records:
                print(record)
        else:
            print("Запрос не вернул данных.")

        return records

    except (Exception, psycopg2.Error) as error:
        print(f"Ошибка при работе с PostgreSQL:", error)
        return []

    finally:
        if connection:
            cursor.close()
            connection.close()


def update_positive_customers(customers):
    """Очищает файл positive_customers_data.py и записывает новые результаты"""
    with open("../Arrays/positive_customers_data.py", "w") as file:
        # Записываем массив в Python-совместимый формат
        file.write(f"positive_customers = {customers}\n")
        print("Файл positive_customers_data.py обновлен.")


# Пример использования функции
data = get_operations_from_db()

# Если запрос вернул данные, обновляем файл
if data:
    # Создаем массив, содержащий как user_id, так и session_key (первое и второе значения из записи)
    positive_customers = [(record[1], record[4]) for record in data]  # Берем id пользователя и session_key

    # Обновляем файл positive_customers_data.py
    update_positive_customers(positive_customers)
else:
    print("Нет данных для обновления positive_customers_data.py.")
