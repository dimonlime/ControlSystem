import os
import requests
import dotenv
import json
from odds.app.parse import get_start_and_end_of_current_month
from datetime import datetime, timedelta

dotenv.load_dotenv()
url_inf = os.getenv('URLINFO')
token_modulbank = os.getenv('TOKEN_API')
url_pay = os.getenv('URLPAY')
url_market = os.getenv('URLMARKETCARD')
date_now = datetime.now().date()
today = datetime.today()
weekday = today.weekday()
last_monday = today - timedelta(days=weekday + 7)
last_sunday = last_monday + timedelta(days=6)
last_monday_str = last_monday.strftime("%Y-%m-%d 00:00:00")
last_sunday_str = last_sunday.strftime("%Y-%m-%d 23:59:59")
startDate, endDate = get_start_and_end_of_current_month(date_now)
headers_modulbank = {
    "Authorization": f"Bearer {token_modulbank}",
    "Content-Type": "application/json"
}

params_modulbank = {
    "from": f"{startDate}",
    "records": 50
}

response_info = requests.post(url_inf, headers=headers_modulbank)
res_pay = requests.post(url_pay, headers=headers_modulbank, json=params_modulbank)
print(json.dumps(res_pay.json(), indent=4, ensure_ascii=False))


token_WB = os.getenv('WB_TOKEN_ANALIT')
url_analit = os.getenv('URL_ANALITIK')

headers_wb = {'Authorization': token_WB,
              'Content-Type': 'application/json'}
params_analit = {'period': {'begin': f"{last_monday_str}", 'end': f"{last_sunday_str}"}, 'page': 1}
response_analit = requests.post(url_analit, headers=headers_wb, json=params_analit)
print(json.dumps(response_analit.json(), indent=4, ensure_ascii=False))
