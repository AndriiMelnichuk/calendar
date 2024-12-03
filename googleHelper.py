import requests
import urllib.parse
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

CLIENT_ID = os.getenv('CLIENT_ID')
CLIENT_SECRET = os.getenv('CLIENT_SECRET')


def day_and_next(date_string):
    if '2099' in date_string:
        date_string = datetime.today().strftime('%Y-%m-%dT%H:%M:%S')

    date_object = datetime.strptime(date_string, "%Y-%m-%dT%H:%M:%S").date()
    date_string = date_object.strftime("%Y-%m-%d")

    
    new_date_object = date_object + timedelta(days=1)
    new_date_string = new_date_object.strftime("%Y-%m-%d")
    return date_string, new_date_string


def day_and_next_utc(date_string):
    if '2099' in date_string:
        # Если в дате указана 2099, используем текущую дату
        date_string = datetime.today().strftime('%Y-%m-%dT%H:%M:%S')

    # Преобразуем строку в объект datetime
    date_object = datetime.strptime(date_string, "%Y-%m-%dT%H:%M:%S")

    # Форматируем дату в нужный формат с временем (UTC)
    date_string_utc = date_object.strftime("%Y-%m-%dT%H:%M:%S") + 'Z'
    
    # Добавляем 1 день
    new_date_object = date_object + timedelta(days=1)
    
    # Форматируем новую дату
    new_date_string_utc = new_date_object.strftime("%Y-%m-%dT%H:%M:%S") + 'Z'
    
    return date_string_utc, new_date_string_utc


def add_event(data, access_token):
    url = 'https://www.googleapis.com/calendar/v3/calendars/primary/events'
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    
    date_string = data['date']
    date_string, new_date_string = day_and_next(date_string)    
    
    event_data = {
        'summary': data['title'],
        # 'location': 'Онлайн',
        'description': data['description'],
        'start': {
            'date': date_string,
        },
        'end': {
            'date': new_date_string,

        },
        'timeZone': 'Europe/Kyiv',
        # 'attendees': [
        #     {'email': 'todofam0@gmail.com'},
        #     {'email': 'example2@gmail.com'}
        # ]
    }
    
    response = requests.post(url, headers=headers, json=event_data)
    if response.status_code == 200:
        print('Событие добавлено успешно!')
    else:
        print('Ошибка:', response.json())


def delete_event(data, access_token):
    if is_at_google(data, access_token):
        events = get_tasks_from_google(data, access_token)
        event_id = 0
        for event in events:
            ev_des = event['description'] if 'description' in event.keys() else ''
            if event['summary'] == data['title'] and ev_des == data['description']:
                event_id = event['id']
        url = f'https://www.googleapis.com/calendar/v3/calendars/primary/events/{event_id}'
        headers = {
            'Authorization': f'Bearer {access_token}',
        }
        response = requests.delete(url, headers=headers)

        if response.status_code == 204:
            print("INFO: DELETE success.")
        else:
            print(f"ERROR: DELETE failed {response.status_code} - {response.text}")
    else:
        print('INFO: Task absent to delete')


def get_tasks_from_google(task, access_token):
    url = 'https://www.googleapis.com/calendar/v3/calendars/primary/events'
    date_string = task['date']
    date_string, new_date_string = day_and_next_utc(date_string)    
    params = {
        'timeMin': date_string,
        'timeMax': new_date_string,
        'singleEvents': 'true',  
        'orderBy': 'startTime',  
    }

    headers = {
        'Authorization': f'Bearer {access_token}',
    }

    response = requests.get(url, headers=headers, params=params)
    
    if response.status_code != 200:
        raise Exception(f"Error fetching events: {response.status_code} - {response.text}")

    events = response.json().get('items', [])
    return events


def is_at_google(task, access_token):
    events = get_tasks_from_google(task, access_token)
    for event in events:
        ev_des = event['description'] if 'description' in event.keys() else ''
        if event['summary'] == task['title'] and ev_des == task['description']:
            return True
    return False 


