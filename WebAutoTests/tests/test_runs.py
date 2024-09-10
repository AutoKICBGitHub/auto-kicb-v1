from playwright.sync_api import sync_playwright
from WebAutoTests.tests.login_automation import LoginAutomation
from WebAutoTests.tests.login_automation import PaymentExchangeUsdKgs
from WebAutoTests.utils.users import get_user

def test_login():
    user = get_user('1')  # Получаем данные пользователя

    with sync_playwright() as playwright:
        automation = LoginAutomation(playwright)
        automation.login_user(user)


def test_exchange():
    with sync_playwright() as playwright:
        exchange = PaymentExchangeUsdKgs(playwright)
        exchange.perform_exchange()
