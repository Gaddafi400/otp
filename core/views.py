from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.core.mail import send_mail
from django.utils.crypto import get_random_string

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


@api_view(['POST'])
def generate_and_send_otp(request):
    email = request.data.get('email')

    if not email:
        return Response({'error': 'Email is required'})

    # Generate 6-digit OTP
    otp_code = get_random_string(length=6, allowed_chars='1234567890')

    # Store OTP in the session
    request.session['otp_code'] = otp_code
    request.session['email'] = email

    # Send OTP via email
    send_mail(
        'Your OTP Code',
        f'Your OTP code is: {otp_code}',
        'test@example.com',
        [email],
        fail_silently=False,
    )

    return Response({'message': 'OTP sent successfully'})


@api_view(['POST'])
def verify_otp(request):
    email = request.data.get('email')
    otp_code = request.data.get('otp_code')

    if not email or not otp_code:
        return Response({'error': 'Email and OTP code are required'})

    # Retrieve OTP from the session
    stored_otp = request.session.get('otp_code')
    stored_email = request.session.get('email')

    if stored_otp and stored_email == email and stored_otp == otp_code:
        # Clear the OTP from the session after successful verification
        request.session.pop('otp_code')
        request.session.pop('email')
        return Response({'message': 'OTP verified successfully'})
    else:
        return Response({'error': 'Invalid OTP'})
