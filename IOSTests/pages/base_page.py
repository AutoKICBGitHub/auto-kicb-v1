from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class BasePage:
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(self.driver, 15)

    def find_element(self, locator):
        return self.wait.until(EC.presence_of_element_located(locator))

    def find_elements(self, locator):
        return self.wait.until(EC.presence_of_all_elements_located(locator))

    def click(self, locator):
        self.find_element(locator).click()

    def send_keys(self, locator, text):
        self.find_element(locator).send_keys(text)

    def is_element_visible(self, locator):
        try:
            self.wait.until(EC.visibility_of_element_located(locator))
            return True
        except:
            return False

    def handle_alerts(self):
        """Обработка системных алертов iOS"""
        try:
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
                    alert = self.wait.until(EC.presence_of_element_located(
                        (AppiumBy.ACCESSIBILITY_ID, button_text)
                    ))
                    alert.click()
                    print(f"✅ Нажата кнопка: {button_text}")
                    return True
                except:
                    continue
                
            # Также проверяем по XPath для случаев, когда accessibility id не работает
            xpath_alert = self.wait.until(EC.presence_of_element_located(
                (AppiumBy.XPATH, "//XCUIElementTypeButton[@name='Allow']")
            ))
            xpath_alert.click()
            print("✅ Разрешение предоставлено через XPath")
            return True
            
        except:
            print("ℹ️ Алерты не найдены или уже обработаны")
            return False
