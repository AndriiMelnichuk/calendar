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

def get_oauth():
    auth_url = 'https://accounts.google.com/o/oauth2/v2/auth'
    params = {
        'nonce' : 'nonce',
        'client_id': CLIENT_ID,
        'redirect_uri': 'http://localhost:5000',
        'response_type': 'id_token code',
        'scope': 'https://www.googleapis.com/auth/calendar.events',
        'access_type': 'offline'
    }
    print(f'Перейдите по ссылке для авторизации: {auth_url}?{urllib.parse.urlencode(params)}')


def oauth2accces_token(autorisation_code):
    token_url = 'https://oauth2.googleapis.com/token'
    data = {
        'code': autorisation_code,  # Код из URL
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'redirect_uri': 'http://localhost:5000',
        'grant_type': 'authorization_code',
    }

    response = requests.post(token_url, data=data)
    if response.ok:
        tokens = response.json()
        access_token = tokens.get('access_token')
        print('Access Token:', access_token)
    else:
        print('Error:', response.json())


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


def is_at_google(task, access_token):
        # Задаем URL для получения событий из календаря
    url = 'https://www.googleapis.com/calendar/v3/calendars/primary/events'
    date_string = task['date']
    date_string, new_date_string = day_and_next_utc(date_string)    
    # Устанавливаем параметры запроса (ищем события на определенную дату)
    params = {
        'timeMin': date_string,  # Начало дня в UTC
        'timeMax': new_date_string,  # Конец дня в UTC
        'singleEvents': 'true',  # Получать все события, включая повторяющиеся
        'orderBy': 'startTime',  # Сортировать по времени начала
    }

    # Устанавливаем заголовки с авторизацией
    headers = {
        'Authorization': f'Bearer {access_token}',  # Ваш токен доступа
    }

    # Отправляем GET запрос
    response = requests.get(url, headers=headers, params=params)
    
    # Проверяем статус ответа
    if response.status_code != 200:
        raise Exception(f"Error fetching events: {response.status_code} - {response.text}")

    # Получаем список событий из ответа
    events = response.json().get('items', [])

    # Проверяем, есть ли событие с нужным summary
    for event in events:
        if event['summary'] == task['title'] and event['description'] == task['description']:
            return True  # Событие найдено
    
    return False  # Событие не найдено

