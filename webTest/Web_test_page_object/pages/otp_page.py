import pyotp
from webTest.Web_test_page_object.utils.users import users

class OtpPage:
    def __init__(self, page):
        self.page = page

    def enter_otp(self, users):
        users_otp = users.get("user1").get("otp_secret")
        totp = pyotp.TOTP(users_otp, interval=30, digest='sha1')
        otp_code = totp.now()
        self.page.locator(".confirm-otp__input").first.wait_for(timeout=30000)
        self.page.locator(".confirm-otp__input").first.click()
        self.page.keyboard.type(otp_code)
