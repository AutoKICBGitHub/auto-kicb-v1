from pages.Exchange_page import ExchangePage1

def test_exchange_flow(browser):
    page = browser
    exchange_page = ExchangePage1(page)
    exchange_page.exchange_1()  # Обменка с доллара на сом
    exchange_page.exchange_2()  # Обменка с сома на доллар


