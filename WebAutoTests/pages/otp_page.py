import pyotp
from WebAutoTests.utils.users import get_user

class OtpPage:
    def __init__(self, page):
        self.page = page

    def enter_otp(self, driver):

        totp = pyotp.TOTP(driver, interval=30, digest='sha1')
        otp_code = totp.now()
        self.page.locator(".confirm-otp__input").first.wait_for(timeout=30000)
        self.page.locator(".confirm-otp__input").first.click()
        self.page.keyboard.type(otp_code)
