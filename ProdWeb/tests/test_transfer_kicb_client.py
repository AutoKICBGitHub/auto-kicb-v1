from pages.Transfer_KICB_page import Transfer_KICB_page1   
import allure

     
@allure.title("Тест перевода клиенту KICB")
@allure.description("Проверка процесса перевода клиенту KICB")
def test_exchange_flow(browser):
        try: 
                page = browser
                # обменка с доллара на сом
                transfer_page = Transfer_KICB_page1(page)
                transfer_page.Transfer_KICB_card()
                transfer_page.Transfer_KICB_phone_nubmer()
                transfer_page.Transfer_KICB_account()
        except Exception as e:
            allure.attach(str(e), name="Ошибка", attachment_type=allure.attachment_type.TEXT)
            raise 
