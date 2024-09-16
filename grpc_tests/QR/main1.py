import pandas as pd
from itertools import product

# Определяем возможные типы пользователей, счетов, филиалов, валют, и тарифов
USER_TYPES = ["INDIVIDUAL", "CORP", "MERCHANT"]
ACCOUNT_TYPES = ["CARD", "SETTLEMENT"]
BRANCHES = ["001", "533"]
CURRENCIES = ["USD", "SOM"]

# Определяем возможные типы тарифов
TARIFFS = [
    ("Global to INDIVIDUAL", "Global to INDIVIDUAL"),
    ("Global to CORP", "Global to CORP"),
    ("Global to MERCHANT", "Global to MERCHANT"),
    ("IND to IND", "IND to IND"),
    ("IND to CORP", "IND to CORP"),
    ("IND to MERCH", "IND to MERCH")
]

# Генерация комбинаций для отправителей
def generate_sender_combinations():
    senders = []
    checked_senders = set()

    for user, account, branch, currency in product(USER_TYPES, ACCOUNT_TYPES, BRANCHES, CURRENCIES):
        if (user, branch, account, currency) not in checked_senders:
            checked_senders.add((user, branch, account, currency))
            senders.append({
                'User From': user,
                'Account From': account,
                'Branch From': branch,
                'Currency From': currency
            })
    return senders

# Генерация комбинаций для получателей
def generate_receiver_combinations():
    receivers = []
    checked_receivers = set()

    for user, account, branch, currency in product(USER_TYPES, ACCOUNT_TYPES, BRANCHES, CURRENCIES):
        if (user, branch, account, currency) not in checked_receivers:
            checked_receivers.add((user, branch, account, currency))
            receivers.append({
                'User To': user,
                'Account To': account,
                'Branch To': branch,
                'Currency To': currency
            })
    return receivers

# Объединение отправителей и получателей
def combine_senders_receivers(senders, receivers):
    transactions = []
    for sender, receiver in product(senders, receivers):
        combined = {**sender, **receiver}
        transactions.append(combined)
    return transactions

# Добавление тарифов к каждой комбинации
def add_tariffs(transactions):
    final_transactions = []
    for transaction in transactions:
        for send_tariff, receive_tariff in TARIFFS:
            final_transaction = transaction.copy()
            final_transaction['Send Tariff'] = send_tariff
            final_transaction['Receive Tariff'] = receive_tariff
            final_transactions.append(final_transaction)
    return final_transactions

# Генерация данных
senders = generate_sender_combinations()
receivers = generate_receiver_combinations()

# Комбинирование отправителей и получателей
combined_transactions = combine_senders_receivers(senders, receivers)

# Добавление тарифов
final_transactions = add_tariffs(combined_transactions)

# Преобразование в DataFrame и сохранение
df_final = pd.DataFrame(final_transactions)
df_final.to_excel('C:/project_kicb/QR/final_optimized_tariff_flows1.xlsx', index=False)


# Вывод количества записей
df_final.shape[0], df_final.sample(10)





