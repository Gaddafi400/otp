from django.urls import path
from .views import login_view, otp_view, main_view, logout_view

app_name = 'core'
urlpatterns = [
    path('', main_view, name='main'),
    path('login/', login_view, name='login-view'),
    path('logout_view/', logout_view, name='logout-view'),
    path('otp/', otp_view, name='otp-view'),
]


