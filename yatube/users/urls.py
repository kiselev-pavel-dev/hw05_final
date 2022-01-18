from django.contrib.auth.views import (LogoutView,
                                       LoginView,
                                       PasswordChangeView,
                                       PasswordChangeDoneView,
                                       PasswordResetView,
                                       PasswordResetDoneView,
                                       PasswordResetConfirmView,
                                       PasswordResetCompleteView)

from django.urls import path

from . import views

app_name = 'users'

PRCT = 'users/password_reset_complete.html'
PRCF = 'users/password_reset_confirm.html'
PRD = 'users/password_reset_done.html'
PRF = 'users/password_reset_form.html'
PCD = 'users/password_change_done.html'
PCV = 'users/password_change_form.html'

urlpatterns = [
    path('logout/',
         LogoutView.as_view(template_name='users/logged_out.html'),
         name='logout'),
    path('signup/', views.SignUp.as_view(),
         name='signup'),
    path('login/', LoginView.as_view(template_name='users/login.html'),
         name='login'),
    path('reset/done/',
         PasswordResetCompleteView.as_view(template_name=PRCT),
         name='reset_done'),
    path('reset/<uidb64>/<token>/',
         PasswordResetConfirmView.as_view(template_name=PRCF),
         name='password_reset_confirm'),
    path('password_reset/done/',
         PasswordResetDoneView.as_view(template_name=PRD),
         name='password_reset_form_done'),
    path('password_reset/',
         PasswordResetView.as_view(template_name=PRF),
         name='password_reset'),
    path('password_change/done/',
         PasswordChangeDoneView.as_view(template_name=PCD),
         name='password_change_done'),
    path('password_change/',
         PasswordChangeView.as_view(template_name=PCV),
         name='password_change'),
]
