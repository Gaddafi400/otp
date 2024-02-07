import pyotp
from datetime import datetime, timedelta


def send_otp(request):
    topt = pyotp.TOTP(pyotp.random_base32(), interval=60)
    otp = topt.now()
    request.session['otp_secret_key'] = topt.secret
    otp_valid_date = datetime.now() + timedelta(minutes=1)
    request.session['otp_valid_date'] = str(otp_valid_date)
    print(f'Your one time password is {otp}')


