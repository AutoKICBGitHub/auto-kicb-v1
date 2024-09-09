class VisaCard:
    def __init__(self, card_number, full_name, expiry_date, security_code, amount_to_transfer):
        self.card_number = card_number
        self.full_name = full_name
        self.expiry_date = expiry_date
        self.security_code = security_code
        self.amount_to_transfer = amount_to_transfer




visa_cards = {
    '1': VisaCard(card_number="4446732000690489", full_name="ANNA MIRONOVA", expiry_date="09/26", security_code="625", amount_to_transfer="1"),
    '2': VisaCard(card_number="4222222222222222", full_name="Jane Doe", expiry_date="11/24", security_code="456", amount_to_transfer="500"),
    # Add more Visa card details as needed
}

def get_visa_card(card_id):
    return visa_cards.get(card_id)
