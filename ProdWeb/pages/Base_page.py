from playwright.sync_api import Page


class BasePage:
    def __init__(self, page: Page):
        self.page = page

    def go_to(self, url: str):
        """Переходит по указанному URL."""  # ЗАДАТЬ: URL для перехода
        self.page.goto(url)

    def click(self, locator: str):
        """Кликает по указанному локатору."""  # ЗАДАТЬ: локатор для клика
        self.page.locator(locator).click()

    def type_text(self, locator: str, text: str):
        """Вводит текст в указанный элемент."""  # ЗАДАТЬ: локатор и текст для ввода
        self.page.locator(locator).fill(text)

    def get_text(self, locator: str) -> str:
        """Возвращает текст элемента."""  # ЗАДАТЬ: локатор для получения текста
        return self.page.locator(locator).inner_text()

    def is_visible(self, locator: str) -> bool:
        """Проверяет, виден ли элемент."""  # ЗАДАТЬ: локатор для проверки видимости
        return self.page.locator(locator).is_visible()

    def wait_for_url(self, url_fragment: str):
        """Ожидает, пока URL изменится."""  # ЗАДАТЬ: фрагмент URL для ожидания
        self.page.wait_for_url(url_fragment)

    def get_locator_by_text(self, text: str) -> str:
        """Возвращает XPath локатор по тексту элемента."""
        return f"//*[text()='{text}']"

    def click_by_text(self, text: str):
        """Кликает по элементу, найденному по тексту."""
        locator = self.get_locator_by_text(text)
        self.page.locator(locator).click()
