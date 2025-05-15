from django.urls import path
from . import views  # Import your views here 

urlpatterns = [
    path('', views.index, name='index'),  # Homepage
    path('login', views.user_login, name='login'),  # Correct the login path to include the trailing slash
    path('signup', views.user_signup, name='signup'),  # Signup path
    path('logout', views.user_logout, name='logout'),  # Logout path
    path('generate-blog', views.generate_blog, name='generate_blog'),
    path('blog-list', views.blog_list, name='blog-list'),
    path('blog-details/<int:pk>', views.blog_details, name='blog-details'),
]