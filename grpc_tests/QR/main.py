import pandas as pd

# Определяем возможные типы пользователей, счетов, филиалов, валют, и тарифов
USER_TYPES = ["INDIVIDUAL", "CORP", "MERCHANT"]
ACCOUNT_TYPES = ["CARD", "SETTLEMENT"]
BRANCHES = ["001", "533"]
CURRENCIES = ["USD", "SOM"]

# Определяем возможные типы тарифов
TARIFFS = {
    "GLOBAL": ["Global to INDIVIDUAL", "Global to CORP", "Global to MERCHANT"],
    "INDIVIDUAL": ["IND to IND", "IND to CORP", "IND to MERCH"]
}

# Тестовая модель
class Transaction:
    def __init__(self, user_from, account_from, branch_from, currency_from, user_to, account_to, branch_to, currency_to, send_tariff, receive_tariff):
        self.user_from = user_from
        self.account_from = account_from
        self.branch_from = branch_from
        self.currency_from = currency_from
        self.user_to = user_to
        self.account_to = account_to
        self.branch_to = branch_to
        self.currency_to = currency_to
        self.send_tariff = send_tariff
        self.receive_tariff = receive_tariff

    def as_dict(self):
        return {
            'User From': self.user_from,
            'Account From': self.account_from,
            'Branch From': self.branch_from,
            'Currency From': self.currency_from,
            'User To': self.user_to,
            'Account To': self.account_to,
            'Branch To': self.branch_to,
            'Currency To': self.currency_to,
            'Send Tariff': self.send_tariff,
            'Receive Tariff': self.receive_tariff
        }

# Генерация данных для записи в Excel
transactions = []
for user_from in USER_TYPES:
    for account_from in ACCOUNT_TYPES:
        for branch_from in BRANCHES:
            for currency_from in CURRENCIES:
                for user_to in USER_TYPES:
                    for account_to in ACCOUNT_TYPES:
                        for branch_to in BRANCHES:
                            for currency_to in CURRENCIES:
                                for send_tariff_group, send_tariffs in TARIFFS.items():
                                    for receive_tariff_group, receive_tariffs in TARIFFS.items():
                                        for send_tariff in send_tariffs:
                                            for receive_tariff in receive_tariffs:
                                                transaction = Transaction(user_from, account_from, branch_from, currency_from,
                                                                          user_to, account_to, branch_to, currency_to,
                                                                          send_tariff, receive_tariff)
                                                transactions.append(transaction.as_dict())

# Создание DataFrame и запись в Excel
df = pd.DataFrame(transactions)
df.to_excel('full_tariff_flows_with_directions.xlsx', index=False)

print("Results have been written to 'full_tariff_flows_with_directions.xlsx'.")
