from pages.Transfer_KICB_page import Transfer_KICB_page1   

def test_exchange_flow(browser):
        page = browser
        # обменка с доллара на сом
        transfer_page = Transfer_KICB_page1(page)
        transfer_page.Transfer_KICB_card()
        transfer_page.Transfer_KICB_phone_nubmer()
        transfer_page.Transfer_KICB_account()
