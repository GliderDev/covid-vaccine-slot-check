import csv
import time
import schedule
import requests
from datetime import datetime, timedelta

DISTRICT_ID = 304 # Kottayam Replace this with your district id form cowin site
TOKEN = '' # Replace this with telegram bot

def get_subscribers():
    result = []
    url = f'https://api.telegram.org/bot{TOKEN}/getUpdates'
    response = requests.get(url).json()
    subscribers = response['result']
    for subscriber in subscribers:
        result.append(str(subscriber['message']['chat']['id']))
    return result

def send_alert(chat_id, message):
    send_text = f'https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id={chat_id}&parse_mode=Markdown&text={message}'
    response = requests.get(send_text)
    return response.json()

def check_appointment_slot():
    subscribers = get_subscribers()
    headers = {
      'authority': 'cdn-api.co-vin.in',
      'pragma': 'no-cache',
      'cache-control': 'no-cache',
      'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="90", "Google Chrome";v="90"',
      'sec-ch-ua-mobile': '?0',
      'upgrade-insecure-requests': '1',
      'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36',
      'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
      'sec-fetch-site': 'none',
      'sec-fetch-mode': 'navigate',
      'sec-fetch-user': '?1',
      'sec-fetch-dest': 'document',
      'accept-language': 'en-GB,en;q=0.9',
    }
    next_day = datetime.now() + timedelta(days=1)
    next_day = next_day.strftime("%d-%m-%Y")
    url = f'https://cdn-api.co-vin.in/api/v2/appointment/sessions/public/calendarByDistrict?district_id={DISTRICT_ID}&date={next_day}'
    res = requests.get(url, headers=headers)
    result = res.json()
    centers = result['centers']
    for center in centers:
        sessions = center['sessions']
        if sessions:
            for session in sessions:
                if session['available_capacity'] > 0:
                    center_name = center['name']
                    center_address = center['address']
                    min_age_limit = session['min_age_limit']
                    available_capacity = session['available_capacity']
                    message = f"Vaccination available at {center_name} {center_address} on {next_day}. Book ASAP! Mininum age: {min_age_limit}, Available Slots: {available_capacity}"
                    for subscriber_id in subscribers:
                        send_alert(subscriber_id, message)
                else:
                    pass

schedule.every(5).minutes.do(check_appointment_slot)

while True:
    schedule.run_pending()
    time.sleep(1)


# check_appointment_slot()

