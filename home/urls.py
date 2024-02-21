from django.urls import path,re_path
from admin_datta import views
from django.contrib.auth import views as auth_views
from home.views import Warner,Index,Stress,Avif,Watermark, Bt
from django.contrib.auth.decorators import login_required


urlpatterns = [
  path('', login_required(Index.as_view()), name='index'),



  # Warner & stress
  path('warner/', login_required(Warner.as_view()), name='warner'),
  re_path('warner/(?P<ip>[0-9_.]+)/(?P<port>[0-9]+)',Warner.warner_request),
  path('stress/',login_required(Stress.as_view()),name='stress'),
  path('stress/',Stress.as_view(),name='stress'),
  re_path('stress/status/',Stress.stress_status,name='stress_status'),
  #avif
  path('avif/',login_required(Avif.as_view()),name='avif'),
  re_path('convert/$', Avif.convert ,name="convert"),
  #bt
  path('bt/',login_required(Bt.as_view()),name='bt'),
  path('bt/<int:input_id>/', login_required(Bt.as_view()), name='delete_input_view'),
  #webp
  path('watermark/',login_required(Watermark.as_view()),name='watermark'),
  path('watermark_convert/',Watermark.waterconvert,name='watermark_convert'),

  # Authentication
  path('accounts/register/', views.UserRegistrationView.as_view(), name='register'),
  path('accounts/login/', views.UserLoginView.as_view(), name='login'),
  path('accounts/logout/', views.logout_view, name='logout'),

  path('accounts/password-change/', views.UserPasswordChangeView.as_view(), name='password_change'),
  path('accounts/password-change-done/', auth_views.PasswordChangeDoneView.as_view(
      template_name='accounts/auth-password-change-done.html'
  ), name="password_change_done"),

  path('accounts/password-reset/', views.UserPasswordResetView.as_view(), name='password_reset'),
  path('accounts/password-reset-confirm/<uidb64>/<token>/',
    views.UserPasswrodResetConfirmView.as_view(), name="password_reset_confirm"
  ),
  path('accounts/password-reset-done/', auth_views.PasswordResetDoneView.as_view(
    template_name='accounts/auth-password-reset-done.html'
  ), name='password_reset_done'),
  path('accounts/password-reset-complete/', auth_views.PasswordResetCompleteView.as_view(
    template_name='accounts/auth-password-reset-complete.html'
  ), name='password_reset_complete'),

  #
  path('profile/', views.profile, name='profile'),
  path('sample-page/', views.sample_page, name='sample_page'),
 
]

