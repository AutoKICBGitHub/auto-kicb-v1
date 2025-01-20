from .base_page import BasePage
from appium.webdriver.common.appiumby import AppiumBy
import time


class TransferKICBPage(BasePage):
    def __init__(self, driver):
        super().__init__(driver)
        # Навигация к переводу
        self.kicb_transfer_button = '//XCUIElementTypeStaticText[@name="Клиенту KICB"]'
        
        # Общие элементы
        self.account_from_field = '//XCUIElementTypeScrollView/XCUIElementTypeOther[1]/XCUIElementTypeOther/XCUIElementTypeOther[1]/XCUIElementTypeOther[1]/XCUIElementTypeOther'
        self.account_from_cell = '(//XCUIElementTypeStaticText[@name="VISA CLASSIC"])[1]'
        self.amount_input = '//XCUIElementTypeScrollView/XCUIElementTypeOther[1]/XCUIElementTypeOther/XCUIElementTypeOther[3]/XCUIElementTypeOther/XCUIElementTypeTextField'
        self.transfer_button = '//XCUIElementTypeButton[@name="Перевести"]'
        self.confirm_button = '//XCUIElementTypeButton[@name="Подтвердить"]'
        self.close_status_button = '//XCUIElementTypeNavigationBar[@name="Статус перевода"]/XCUIElementTypeButton'
        
        # Типы перевода
        self.by_account_tab = '//XCUIElementTypeButton[@name="Счет"]'
        self.by_card_tab = '//XCUIElementTypeButton[@name="Карта"]'
        self.by_phone_tab = '//XCUIElementTypeButton[@name="Телефон"]'
        
        # Поля ввода для разных типов
        self.account_input = '//XCUIElementTypeTextField[@value="Номер счета"]'
        self.card_input = '//XCUIElementTypeTextField[@value="Номер карты"]'
        self.phone_input = '//XCUIElementTypeTextField[@value="Номер телефона"]'
        
        # Клавиатура и заголовок
        self.keyboard_done_button = '//XCUIElementTypeButton[@name="Done"]'
        self.page_title = '//XCUIElementTypeStaticText[@name="Клиенту KICB"]'

    def navigate_to_kicb_transfer(self):
        """Переход к переводу клиенту KICB"""
        self.wait_for_element_to_be_visible(self.kicb_transfer_button)
        self.click_element(self.kicb_transfer_button)
        print("✅ Выполнен переход к переводу клиенту KICB")

    def select_source_account(self):
        """Выбор счета списания"""
        try:
            # Нажимаем на поле выбора счета
            self.click_element(self.account_from_field)
            time.sleep(1)  # Даем время на открытие списка
            
            # Ждем появления и выбираем нужную карту/счет
            account_cell = self.wait_for_element_to_be_visible(self.account_from_cell)
            account_cell.click()
            print("✅ Выбран счет списания")
            return True
        except Exception as e:
            print(f"❌ Ошибка при выборе счета списания: {e}")
            return False

    def hide_keyboard(self):
        """Скрытие клавиатуры"""
        try:
            # Сначала пробуем нажать кнопку Done
            self.click_element(self.keyboard_done_button)
            print("✅ Клавиатура скрыта кнопкой Done")
        except:
            try:
                # Если кнопка Done не найдена, тапаем по заголовку
                self.click_element(self.page_title)
                print("✅ Клавиатура скрыта тапом по заголовку")
            except Exception as e:
                print(f"❌ Ошибка при скрытии клавиатуры: {e}")

    def transfer_by_account(self, account_number, amount="1"):
        """Перевод по номеру счета"""
        self.navigate_to_kicb_transfer()
        self.click_element(self.by_account_tab)
        self.select_source_account()
        self.send_keys_to_element(self.account_input, account_number)
        self.send_keys_to_element(self.amount_input, amount)
        self.hide_keyboard()  # Скрываем клавиатуру
        self._complete_transfer()
        print(f"✅ Выполнен перевод {amount} сом на счет {account_number}")

    def transfer_by_card(self, card_number, amount="1"):
        """Перевод по номеру карты"""
        self.navigate_to_kicb_transfer()
        self.click_element(self.by_card_tab)
        self.select_source_account()
        self.send_keys_to_element(self.card_input, card_number)
        self.send_keys_to_element(self.amount_input, amount)
        self.hide_keyboard()  # Скрываем клавиатуру
        self._complete_transfer()
        print(f"✅ Выполнен перевод {amount} сом на карту {card_number}")

    def transfer_by_phone(self, phone_number, amount="1"):
        """Перевод по номеру телефона"""
        self.navigate_to_kicb_transfer()
        self.click_element(self.by_phone_tab)
        self.select_source_account()
        self.send_keys_to_element(self.phone_input, phone_number)
        self.send_keys_to_element(self.amount_input, amount)
        self.hide_keyboard()  # Скрываем клавиатуру
        self._complete_transfer()
        print(f"✅ Выполнен перевод {amount} сом на телефон {phone_number}")

    def _complete_transfer(self):
        """Завершение перевода (нажатие кнопок Перевести и Подтвердить)"""
        self.click_element(self.transfer_button)
        self.click_element(self.confirm_button)
        
        # Ждем исчезновения уведомления
        self.wait_for_notification_to_disappear()
        time.sleep(2)  # Дополнительное ожидание после исчезновения уведомления
        
        try:
            # Пытаемся закрыть экран статуса
            self.click_element(self.close_status_button)
            print("✅ Закрыт экран статуса перевода")
            time.sleep(1)
            
            # Проверяем, не открылся ли центр уведомлений
            notification_center = '//XCUIElementTypeNavigationBar[@name="Notification Center"]'
            try:
                if self.driver.find_element(AppiumBy.XPATH, notification_center).is_displayed():
                    print("ℹ️ Открыт центр уведомлений, закрываем...")
                    # Нажимаем крестик в центре уведомлений
                    close_notification = '//XCUIElementTypeButton[@name="Close"]'
                    self.click_element(close_notification)
                    time.sleep(1)
                    # Повторно пытаемся закрыть экран статуса
                    self.click_element(self.close_status_button)
                    print("✅ Закрыт экран статуса после закрытия уведомлений")
            except:
                # Если центр уведомлений не найден, значит мы успешно закрыли статус
                pass
                
        except Exception as e:
            print(f"❌ Ошибка при закрытии экрана статуса: {e}")
            # Пробуем альтернативный способ закрытия
            try:
                size = self.driver.get_window_size()
                x = size['width'] * 0.1
                y = size['height'] * 0.1
                self.driver.tap([(x, y)])
                print("✅ Закрыт экран статуса альтернативным способом")
            except:
                print("❌ Не удалось закрыть экран статуса") 