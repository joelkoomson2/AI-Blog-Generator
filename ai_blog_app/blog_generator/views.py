from django.shortcuts import render

# Create your views here.
def index(request):
    return render(request, 'index.html') # Render the index.html template to return to the homepage 

def user_login(request):
    return render(request, 'login.html') # Render the login.html template to return to the login page

def user_signup(request):
    return render(request, 'signup.html') # Render the signup.html template to return to the signup page

def user_logout(request):
    pass
