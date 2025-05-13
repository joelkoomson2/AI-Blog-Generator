from django.urls import path
from . import views  # Import your views here 

urlpatterns = [
    path('', views.index, name= 'index'),# Add your URL patterns here
    path('login', views.user_login, name= 'login'),# Add your URL patterns here
    path('signup', views.user_signup, name= 'signup') ,# Add your URL patterns here
    path('logout', views.user_logout, name= 'logout'),# Add your URL patterns here
]