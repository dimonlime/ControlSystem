from datetime import datetime, timedelta
from app.database import requests as rq


async def fire_cheques_check():
    data = await rq.all_cheques()
    for cheque in data:
        cheque_date = datetime.strptime(cheque.cheque_date, "%d-%m-%Y %H:%M")
        today_date = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
        today_date_valid = datetime.strptime(today_date, "%d-%m-%Y %H:%M:%S")
        half_year = today_date_valid - timedelta(days=365 / 2)
        if half_year <= cheque_date <= today_date_valid:
            if (datetime.now() - cheque_date) >= timedelta(days=14) and cheque.cheque_status == 'По чеку имеется отсрочка':
                await rq.set_cheque_status(cheque.id, 'Чек не оплачен по истечению 2 недель',
                                           datetime.now().strftime("%d-%m-%Y %H:%M:%S"))
