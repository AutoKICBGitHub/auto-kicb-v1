from pages.phone_top_up_page import Top_up_Page

import allure

     
@allure.title("Тест пополнения баланса Мегаком")
@allure.description("Проверка процесса пополнения баланса Мегаком")
def test_mobile_top_up(browser):
     try: 
          page = browser
          top_up = Top_up_Page(page)
          top_up.mobile_top_up()
     except Exception as e:
            allure.attach(str(e), name="Ошибка", attachment_type=allure.attachment_type.TEXT)
            raise 