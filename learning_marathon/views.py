from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.contrib import messages
from django.template.defaulttags import register
from pytz import timezone
from . import make_statistics
import datetime


@register.filter
def get_range(value):
    return range(value)

from .models import User, LearningSession
# Create your views here.

def index(request):
    if not request.user.is_authenticated:
        return render(request, 'learning_marathon/login.html')
    if request.method == 'POST':
        if request.user.now_learning:
            current_session = LearningSession.objects.filter(user=request.user).last()
            current_session.end_date = datetime.datetime.now(tz=timezone('Europe/Warsaw'))
            current_session.save()
            request.user.now_learning = False
            request.user.save()
        else:
            current_session = LearningSession.objects.create(user = request.user)
            current_session.save()
            request.user.now_learning = True
            request.user.save()
            return HttpResponseRedirect(reverse('learning_marathon:index'))

    not_available = False
    current_learner = None
    users = User.objects.all()
    for user in users:
        if user.now_learning and user.id != request.user.id:
            not_available = True
            current_learner = user

    return render(request, 'learning_marathon/index.html', {'not_available':not_available, 'current_learner':current_learner})

@login_required
def statistics(request):
    make_statistics.update()
    data = make_statistics.get_data()
    data = data[1:]
    users = User.objects.all()
    return render(request, 'learning_marathon/statistics.html', {'data':data, 'users':users})

def login_view(request):
    if request.method == "POST":

        username = request.POST['email']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse('learning_marathon:index'))
        else:
            return render (request,
                        'learning_marathon/login.html',
                        {'error_message': f'Invalid credentials :-(, {username}, {password}'}
                    )

    return render(request, 'learning_marathon/login.html')

def register(request):
    if request.method == 'POST':
        first_name = request.POST['first-name']
        username = request.POST['email']
        password = request.POST['password']
        confirmation = request.POST['confirmation']

        if password != confirmation:
            return render (request,
                        'learning_marathon/register.html',
                        {'error_message': 'Password must match!  :-('}
                    )

        new_user = User.objects.create_user(first_name = first_name, username = username, password = password)
        new_user.save()
        login(request, new_user)
        return render (request,
                        'learning_marathon/index.html',
                        {'success_message': 'Congratulations! Registration successful :-)'}
                    )

    return render(request, 'learning_marathon/register.html')

def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse('learning_marathon:login'))