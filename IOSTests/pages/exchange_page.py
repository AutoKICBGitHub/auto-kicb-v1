from .base_page import BasePage
import time
from appium.webdriver.common.appiumby import AppiumBy


class ExchangePage(BasePage):
    def __init__(self, driver):
        super().__init__(driver)
        # Навигация
        self.exchange_button = '//XCUIElementTypeStaticText[@name="Обмен валют"]'
        
        # Выбор счетов
        self.account_from_field = '//XCUIElementTypeScrollView/XCUIElementTypeOther[1]/XCUIElementTypeOther/XCUIElementTypeOther[1]/XCUIElementTypeOther[1]/XCUIElementTypeOther'
        self.account_to_field = '//XCUIElementTypeScrollView/XCUIElementTypeOther[1]/XCUIElementTypeOther/XCUIElementTypeOther[2]/XCUIElementTypeOther[1]/XCUIElementTypeOther'
        
        # Счета
        self.som_account = '//XCUIElementTypeStaticText[contains(@name, "1280016059196988")]'
        self.dollar_account = '//XCUIElementTypeStaticText[contains(@name, "1285330003310291")]'
        
        # Поле суммы и кнопки
        self.amount_input = '//XCUIElementTypeScrollView/XCUIElementTypeOther[1]/XCUIElementTypeOther/XCUIElementTypeOther[3]/XCUIElementTypeOther/XCUIElementTypeTextField'
        self.exchange_action_button = '//XCUIElementTypeButton[@name="Обменять"]'
        self.confirm_button = '//XCUIElementTypeButton[@name="Подтвердить"]'
        
        # Клавиатура
        self.keyboard_done_button = '//XCUIElementTypeButton[@name="Done"]'
        
        # Кнопка закрытия статуса
        self.close_status_button = '//XCUIElementTypeNavigationBar[@name="Статус обмена"]/XCUIElementTypeButton[contains(@name, "Назад") or contains(@name, "Close")]'

    def navigate_to_exchange(self):
        """Переход к обмену валют"""
        try:
            self.click_element(self.exchange_button)
            print("✅ Выполнен переход к обмену валют")
            time.sleep(1)  # Ждем загрузку страницы
        except Exception as e:
            print(f"❌ Ошибка при переходе к обмену валют: {e}")

    def _complete_exchange(self):
        """Завершение обмена и закрытие экрана статуса"""
        try:
            # Подтверждение обмена
            self.click_element(self.exchange_action_button)
            time.sleep(1)
            self.click_element(self.confirm_button)
            
            # Ждем исчезновения уведомления
            self.wait_for_notification_to_disappear()
            time.sleep(2)  # Дополнительное ожидание после исчезновения уведомления
            
            try:
                # Пытаемся закрыть экран статуса
                self.click_element(self.close_status_button)
                print("✅ Закрыт экран статуса обмена")
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
        except Exception as e:
            print(f"❌ Ошибка при завершении обмена: {e}")

    def exchange_som_to_dollar(self, amount="10"):
        """Обмен сомов на доллары"""
        try:
            # Переход к обмену валют
            self.navigate_to_exchange()
            
            # Выбор счета списания (сом)
            self.click_element(self.account_from_field)
            time.sleep(1)
            self.click_element(self.som_account)
            
            # Выбор счета пополнения (доллар)
            self.click_element(self.account_to_field)
            time.sleep(1)
            self.click_element(self.dollar_account)
            
            # Ввод суммы
            self.send_keys_to_element(self.amount_input, amount)
            self.click_element(self.keyboard_done_button)
            
            # Завершение обмена
            self._complete_exchange()
            print(f"✅ Выполнен обмен {amount} сом на доллары")
            
        except Exception as e:
            print(f"❌ Ошибка при обмене сом->доллар: {e}")

    def exchange_dollar_to_som(self, amount="0.11"):
        """Обмен долларов на сомы"""
        try:
            # Переход к обмену валют
            self.navigate_to_exchange()
            
            # Выбор счета списания (доллар)
            self.click_element(self.account_from_field)
            time.sleep(1)
            self.click_element(self.dollar_account)
            
            # Выбор счета пополнения (сом)
            self.click_element(self.account_to_field)
            time.sleep(1)
            self.click_element(self.som_account)
            
            # Ввод суммы
            self.send_keys_to_element(self.amount_input, amount)
            self.click_element(self.keyboard_done_button)
            
            # Завершение обмена
            self._complete_exchange()
            print(f"✅ Выполнен обмен {amount} долларов на сомы")
            
        except Exception as e:
            print(f"❌ Ошибка при обмене доллар->сом: {e}") 