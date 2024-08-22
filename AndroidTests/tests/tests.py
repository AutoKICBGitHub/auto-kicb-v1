import pytest
import time
from AndroidTests.pages.login_page import footer_main_page
from AndroidTests.pages.payments_page import payments_top_up
from AndroidTests.pages.Visa_AFT import Visa_AFT
from AndroidTests.Visa_card_info import get_visa_card
class VisaAFT:
    def test_enter_visa_details(driver):
        AFT = Visa_AFT(driver)
        footer_main_page.payments_button.click()
        payments_top_up.Visa_top_up_button.click()
        card = get_visa_card('Anna_Mironova')
        AFT.click(Visa_AFT.bank_account_parent_layout_AFT)
        AFT.enter_text(Visa_AFT.card_number_input_AFT, card.card_number)
        AFT.enter_text(Visa_AFT.full_name_AFT, card.full_name)
        AFT.enter_text(Visa_AFT.expiry_date_AFT, card.expiry_date)
        AFT.enter_text(Visa_AFT.security_code_AFT, card.security_code)
        AFT.enter_text(Visa_AFT.amount_to_transfer_AFT, card.amount_to_transfer)
        AFT.click(Visa_AFT.submit_button_AFT)
        time.sleep(2)
