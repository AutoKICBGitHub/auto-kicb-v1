from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class BasePage:
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(self.driver, 15)

    def wait_for_element_to_be_visible(self, locator, timeout=15):
        """Ожидание видимости элемента"""
        wait = WebDriverWait(self.driver, timeout)
        return wait.until(EC.visibility_of_element_located((AppiumBy.XPATH, locator)))

    def find_element_by_accessibility_id(self, locator):
        """Поиск элемента по accessibility id"""
        return self.wait.until(EC.presence_of_element_located((AppiumBy.ACCESSIBILITY_ID, locator)))

    def find_element_by_xpath(self, locator):
        """Поиск элемента по xpath"""
        return self.wait.until(EC.presence_of_element_located((AppiumBy.XPATH, locator)))

    def click_element(self, locator, locator_type=AppiumBy.XPATH):
        """Клик по элементу"""
        element = self.wait.until(EC.element_to_be_clickable((locator_type, locator)))
        element.click()

    def send_keys_to_element(self, locator, text, locator_type=AppiumBy.XPATH):
        """Ввод текста в элемент"""
        element = self.wait.until(EC.presence_of_element_located((locator_type, locator)))
        element.clear()
        element.send_keys(text)

    def handle_alerts(self):
        """Обработка системных алертов iOS с коротким таймаутом"""
        try:
            # Создаем отдельный wait с коротким таймаутом для алертов
            alert_wait = WebDriverWait(self.driver, 5)  # Уменьшаем таймаут до 5 секунд
            
            # Список возможных текстов кнопок разрешения
            allow_buttons = [
                "Allow",
                "OK",
                "Разрешить",
                "Allow Once",
                "While Using the App"
            ]
            
            for button_text in allow_buttons:
                try:
                    alert = alert_wait.until(EC.presence_of_element_located(
                        (AppiumBy.ACCESSIBILITY_ID, button_text)
                    ))
                    alert.click()
                    print(f"✅ Нажата кнопка: {button_text}")
                    return True
                except:
                    continue
                
            # Также проверяем по XPath с тем же коротким таймаутом
            xpath_alert = alert_wait.until(EC.presence_of_element_located(
                (AppiumBy.XPATH, "//XCUIElementTypeButton[@name='Allow']")
            ))
            xpath_alert.click()
            print("✅ Разрешение предоставлено через XPath")
            return True
            
        except:
            print("ℹ️ Алерты не найдены или уже обработаны")
            return False
