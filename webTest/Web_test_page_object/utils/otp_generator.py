import pyotp

def generate_otp(secret):
    totp = pyotp.TOTP(secret, interval=30, digest='sha1')
    return totp.now()
