from .base_page import BasePage
from selenium.webdriver.support import expected_conditions as EC
from appium.webdriver.common.appiumby import AppiumBy
import time


class LoaderPage(BasePage):
    def __init__(self, driver):
        super().__init__(driver)
        self.loader = '//XCUIElementTypeActivityIndicator'
        self.splash_screen = '//XCUIElementTypeImage[@name="SplashScreen"]'
    
    def wait_for_loader_to_disappear(self, timeout=30):
        """Ожидание исчезновения всех лоадеров"""
        try:
            # Ждем пока пропадет сплэш скрин
            self.wait.until(EC.invisibility_of_element_located(
                (AppiumBy.XPATH, self.splash_screen)
            ))
            
            # Ждем пока пропадут все лоадеры
            self.wait.until(EC.invisibility_of_element_located(
                (AppiumBy.XPATH, self.loader)
            ))
            print("✅ Загрузочный экран пройден")
            return True
        except:
            print("❌ Проблема с загрузочным экраном")
            return False 