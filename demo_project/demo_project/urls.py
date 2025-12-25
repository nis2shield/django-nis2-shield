from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('spam/', views.spam, name='spam'),
    path('protected/', views.protected, name='protected'),
    path('mfa/verify/', views.mfa_verify, name='mfa_verify'),
]
