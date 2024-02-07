import pyotp
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import logout, authenticate, login
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from datetime import datetime
from .utils import send_otp


# Create your views here.
@login_required
def main_view(request):
    return render(request, 'main.html')


def login_view(request):
    error_message = None
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            send_otp(request)
            request.session['username'] = username
            return redirect('core:otp-view')
        else:
            error_message = 'Invalid username or password'
    return render(request, 'login.html', {'error_message': error_message})


def otp_view(request):
    error_message = None
    if request.method == 'POST':
        otp = request.POST['otp']
        username = request.session['username']
        otp_secret_key = request.session['otp_secret_key']
        otp_valid_date = request.session['otp_valid_date']
        if otp_secret_key and otp_valid_date is not None:
            valid_until = datetime.fromisoformat(otp_valid_date)
            if valid_until > datetime.now():
                totp = pyotp.TOTP(otp_secret_key, interval=60)
                if totp.verify(otp):
                    user = get_object_or_404(User, username=username)
                    login(request, user)
                    del request.session['otp_secret_key']
                    del request.session['otp_valid_date']
                    return redirect('core:main')
                else:
                    error_message = 'invalid onetime password'.capitalize()
            else:
                error_message = 'onetime password has expired'.capitalize()
        else:
            error_message = 'ups.. something went wrong'.capitalize()
    return render(request, 'otp.html', context={'error_message': error_message})


def logout_view(request):
    logout(request)
    return redirect('core:login-view')
