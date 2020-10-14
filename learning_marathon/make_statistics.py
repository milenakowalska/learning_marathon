import json
from .models import User, LearningSession
import datetime
import os
import re

def day_summary(user, date):
    entries = LearningSession.objects.filter(user=user)
    day_complete = datetime.timedelta(seconds=0)

    for entry in entries:
        if entry.start_date.day == date.day and entry.start_date.month == date.month and entry.start_date.year == date.year:
            day_complete += entry.duration()

    return day_complete - datetime.timedelta(microseconds=day_complete.microseconds)

def new_data(date):
    user1 = User.objects.first()
    user2 = User.objects.last()

    day_entry = {
        'day':date.isoformat(),
        'user1':str(day_summary(user1, date)),
        'user2':str(day_summary(user2, date)),
        'user1_rewards':str(day_summary(user1, date).seconds//3600),
        'user2_rewards':str(day_summary(user2, date).seconds//3600)
    }
    return day_entry

def add_daily_summary(new_data):
    with open (os.path.join(os.path.dirname(__file__),'learning_sessions.json')) as json_file:
        data = json.load(json_file)
        learning_sessions = data['learning_sessions']
        learning_sessions.append(new_data)
    
    with open (os.path.join(os.path.dirname(__file__),'learning_sessions.json'), 'w') as json_file:
        json.dump(data, json_file)


def update():
    with open (os.path.join(os.path.dirname(__file__),'learning_sessions.json')) as json_file:
        data = json.load(json_file)
        last_update = data['learning_sessions'][-1]['day']
        if ((datetime.date.fromisoformat(last_update).day != (datetime.date.today().day)) and datetime.datetime.now().hour > 7):
            new_entry = new_data(datetime.date.today())
            add_daily_summary(new_entry)

def get_data():
    with open (os.path.join(os.path.dirname(__file__),'learning_sessions.json')) as json_file:
        data = json.load(json_file)
        learning_sessions = data['learning_sessions']
        for session in learning_sessions:
            time_user1 = datetime.datetime.strptime(session['user1'],"%H:%M:%S")
            duration = datetime.timedelta(hours=time_user1.hour, minutes=time_user1.minute, seconds=time_user1.second)
            session['user1'] = duration
            session['user1_rewards'] = int(session['user1_rewards'])

            time_user2 = datetime.datetime.strptime(session['user2'],"%H:%M:%S")
            duration = datetime.timedelta(hours=time_user2.hour, minutes=time_user2.minute, seconds=time_user2.second)
            session['user2'] = duration
            session['user2_rewards'] = int(session['user2_rewards'])

    return learning_sessions