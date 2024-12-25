from pages.Internet_top_up_page import Intenet_and_tv_top_up_Page
import allure

     
@allure.title("Тест пополнения счета Aknet")
@allure.description("Проверка процесса пополнения счета через Aknet")
def test_aknet_top_up(browser):
     try:
          page = browser
          top_up = Intenet_and_tv_top_up_Page(page)
          top_up.intenet_top_up_aknet()
     except Exception as e:
            allure.attach(str(e), name="Ошибка", attachment_type=allure.attachment_type.TEXT)
            raise     