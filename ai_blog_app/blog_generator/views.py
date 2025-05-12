from django.shortcuts import render

# Create your views here.
def index(request):
    return render(request, 'index.html') # Render the index.html template to return to the homepage 
