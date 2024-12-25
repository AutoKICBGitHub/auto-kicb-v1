from pages.Exchange_page import ExchangePage1
import allure

     
@allure.title("Тест обмена валют")
@allure.description("Проверка процесса обмена валют")
def test_exchange_flow(browser):
    try:    
        page = browser
        exchange_page = ExchangePage1(page)
        exchange_page.exchange_1()  # Обменка с доллара на сом
        exchange_page.exchange_2()  # Обменка с сома на доллар
    except Exception as e:
            allure.attach(str(e), name="Ошибка", attachment_type=allure.attachment_type.TEXT)
            raise 

