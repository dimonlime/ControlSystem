from datetime import datetime, timedelta
from app.database import requests as rq
from app.utils.utils import half_year_check_cheques


async def fire_cheques_check():
    data = await rq.all_cheques()
    for cheque in data:
        cheque_date = datetime.strptime(cheque.cheque_date, "%d-%m-%Y %H:%M")
        if await half_year_check_cheques(cheque.cheque_date):
            if (datetime.now() - cheque_date) >= timedelta(days=14) and cheque.cheque_status == 'По чеку имеется отсрочка':
                await rq.set_cheque_status(cheque.id, 'Чек не оплачен по истечению 2 недель',
                                           datetime.now().strftime("%d-%m-%Y %H:%M:%S"))
