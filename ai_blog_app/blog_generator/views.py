from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.conf import settings
import json
from pytube import YouTube
import os
import assemblyai as aai
import google.generativeai as genai
from .models import BlogPost
import subprocess
import uuid

# Create your views here.
@login_required
def index(request):
    return render(request, 'index.html')

@csrf_exempt
def generate_blog(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            yt_link = data['link']
        except (KeyError, json.JSONDecodeError):
            return JsonResponse({'error': 'Invalid data sent'}, status=400)

        # get yt title
        title = yt_title(yt_link)
        if not title:
            return JsonResponse({'error': 'Failed to fetch YouTube title. The link may be invalid or YouTube is blocking access.'}, status=400)

        # get transcript
        transcription = get_transcription(yt_link)
        if not transcription:
            return JsonResponse({'error': "Failed to get transcript. Audio download or transcription failed."}, status=500)

        # use Any API key you want to generate the blog I used Google GenAI
        blog_content = generate_blog_from_transcription(transcription)
        if not blog_content:
            return JsonResponse({'error': "Failed to generate blog article"}, status=500)

        # save blog article to database
        new_blog_article = BlogPost.objects.create(
            user=request.user,
            youtube_title=title,
            youtube_link=yt_link,
            generated_content=blog_content,
        )
        new_blog_article.save()

        # return blog article as a response
        return JsonResponse({'content': blog_content})
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=405)

def yt_title(link):
    try:
        # Use yt-dlp to fetch video metadata
        result = subprocess.run([
            "yt-dlp",
            "--get-title",
            link
        ], capture_output=True, text=True, check=True)
        title = result.stdout.strip()
        return title
    except Exception as e:
        print(f"Error in yt_title (yt-dlp): {e}")
        return None

def download_audio(link):
    try:
        output_path = settings.MEDIA_ROOT
        filename = f"{uuid.uuid4()}.mp3"
        output_file = os.path.join(output_path, filename)
        subprocess.run([
            "yt-dlp",
            "-x",
            "--audio-format", "mp3",
            "-o", output_file,
            link
        ], check=True)
        return output_file
    except Exception as e:
        print(f"Error in download_audio (yt-dlp): {e}")
        return None

def get_transcription(link):
    audio_file = download_audio(link)
    if not audio_file:
        print("Failed to download audio for transcription.")
        return None
    aai.settings.api_key = "9d6fc0137e774b1ca62e32232385fd5e"
    try:
        transcriber = aai.Transcriber()
        transcript = transcriber.transcribe(audio_file)
        return transcript.text
    except Exception as e:
        print(f"Error in get_transcription: {e}")
        return None

def generate_blog_from_transcription(transcription):
    # For google-generativeai >=0.3.0, use genai.configure not genai.api_key
    genai.configure(api_key="AIzaSyBsFTLaPoaMZAH4U0freuFLjpD3bdPkkA0")

    prompt = f"Based on the following transcript from a YouTube video, write a comprehensive blog article, write it based on the transcript, but dont make it look like a youtube video, make it look like a proper blog article:\n\n{transcription}\n\nArticle:"

    model = genai.GenerativeModel("gemini-1.5-flash")  # or "gemini-pro" if you have access
    response = model.generate_content(prompt)
    generated_content = response.text.strip()
    return generated_content

def blog_list(request):
    blog_articles = BlogPost.objects.filter(user=request.user)
    return render(request, 'all-blogs.html', {'blog_articles': blog_articles})

def blog_details(request, pk):
    blog_article_detail = BlogPost.objects.get(id=pk)
    if request.user == blog_article_detail.user:
        return render(request, 'blog-details.html', {'blog_article_detail': blog_article_detail})
    else:
        return redirect('/')
    
def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('/')
        else:
            error_message = "Invalid username or password"
            return render(request, 'login.html', {'error_message': error_message})
        
    return render(request, 'login.html')

def user_signup(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        repeatPassword = request.POST['repeatPassword']

        if password == repeatPassword:
            try:
                user = User.objects.create_user(username, email, password)
                user.save()
                login(request, user)
                return redirect('/')
            except:
                error_message = 'Error creating account'
                return render(request, 'signup.html', {'error_message':error_message})
        else:
            error_message = 'Password do not match'
            return render(request, 'signup.html', {'error_message':error_message})
        
    return render(request, 'signup.html')

def user_logout(request):
    logout(request)
    return redirect('/')