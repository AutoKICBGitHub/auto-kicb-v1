from pages.banks_transfers_page import BanksTransfersPage
import allure
from time import sleep

class TestBankTransfers:
    
    @allure.feature("Банковские переводы")
    @allure.story("Переводы в Оптима Банк")
    def test_optima_transfer(self, browser):
        """Тест перевода в Оптима Банк"""
        with allure.step("Выполняем перевод в Оптима Банк"):
            page = browser
            banks_page = BanksTransfersPage(page)
            banks_page.open_banks_transfers()
            banks_page.transfer_to_bank("optima", "996555515516")

    @allure.feature("Банковские переводы")
    @allure.story("Переводы в MBank")
    def test_mbank_transfer(self, browser):
        """Тест перевода в MBank"""
        with allure.step("Выполняем перевод в MBank"):
            page = browser
            banks_page = BanksTransfersPage(page)
            banks_page.open_banks_transfers()
            banks_page.transfer_to_bank("mbank", "996555515516")

    @allure.feature("Банковские переводы")
    @allure.story("Переводы в Бакай Банк")
    def test_bakai_transfer(self, browser):
        """Тест перевода в Бакай Банк"""
        with allure.step("Выполняем перевод в Бакай Банк"):
            page = browser
            banks_page = BanksTransfersPage(page)
            banks_page.open_banks_transfers()
            banks_page.transfer_to_bank("bakai", "996555515516")

    @allure.feature("Банковские переводы")
    @allure.story("Переводы в SimBank")
    def test_simbank_transfer(self, browser):
        """Тест перевода в SimBank"""
        with allure.step("Выполняем перевод в SimBank"):
            page = browser
            banks_page = BanksTransfersPage(page)
            banks_page.open_banks_transfers()
            banks_page.transfer_to_bank("simbank", "996502323335")

    @allure.feature("Банковские переводы")
    @allure.story("Переводы в Демир Банк")
    def test_demir_transfer(self, browser):
        """Тест перевода в Демир Банк"""
        with allure.step("Выполняем перевод в Демир Банк"):
            page = browser
            banks_page = BanksTransfersPage(page)
            banks_page.open_banks_transfers()
            banks_page.transfer_to_bank("demir", "996502323335")

    @allure.feature("Банковские переводы")
    @allure.story("Переводы в Банк Компаньон")
    def test_kompanion_transfer(self, browser):
        """Тест перевода в Банк Компаньон"""
        with allure.step("Выполняем перевод в Банк Компаньон"):
            page = browser
            banks_page = BanksTransfersPage(page)
            banks_page.open_banks_transfers()
            banks_page.transfer_to_bank("kompanion", "996502323335")

    @allure.feature("Банковские переводы")
    @allure.story("Переводы в Айыл Банк")
    def test_ayil_transfer(self, browser):
        """Тест перевода в Айыл Банк"""
        with allure.step("Выполняем перевод в Айыл Банк"):
            page = browser
            banks_page = BanksTransfersPage(page)
            banks_page.open_banks_transfers()
            banks_page.transfer_to_bank("ayil", "996504444342")

    @allure.feature("Банковские переводы")
    @allure.story("Переводы в O!Bank")
    def test_obank_transfer(self, browser):
        """Тест перевода в O!Bank"""
        with allure.step("Выполняем перевод в O!Bank"):
            page = browser
            banks_page = BanksTransfersPage(page)
            banks_page.open_banks_transfers()
            banks_page.transfer_to_bank("obank", "996502323335") 