from webTest.Web_test_page_object.utils import users

class LoginPage:
    def __init__(self, page):
        self.page = page

    def navigate(self):
        self.page.goto("https://ibank.kicb.net/login")

    def login(self, username, password):
        self.page.locator("input[type=\"text\"]").wait_for(timeout=30000)
        self.page.locator("input[type=\"text\"]").fill(username)
        self.page.locator("input[type=\"text\"]").press("Tab")
        self.page.locator("input[type=\"password\"]").wait_for(timeout=30000)
        self.page.locator("input[type=\"password\"]").fill(password)
        self.page.locator("input[type=\"password\"]").press("Enter")
