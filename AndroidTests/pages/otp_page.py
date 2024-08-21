from AndroidTests.utils.adb_utils import ADBUtils

class OTPPage:
    def __init__(self):
        self.adb = ADBUtils()
    otp = "111111"

    def enter_otp(user, otp):
        user.adb.enter_text_via_adb(otp)
