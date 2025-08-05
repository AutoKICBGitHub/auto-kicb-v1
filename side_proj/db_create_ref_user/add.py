import psycopg2

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

def add_multiple_referrals(count=10):
    fixed_user_id = '3145'
    for i in range(count):
        success = add_single_referral('XYJZ8MXST0MV6G6SI3I47PW8WGIP', fixed_user_id, '3085')
        if not success:
            print(f"Ошибка при добавлении записи {i+1}")
            break
        print(f"Добавлена запись {i+1} из {count}")
    print(f"Завершено добавление {count} записей")

if __name__ == "__main__":
    add_multiple_referrals(100)


