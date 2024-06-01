from datetime import datetime, timedelta
from app.database.requests import order_request as order_rq
from app.database.requests import cheque_request as cheque_rq
from app.utils.utils import half_year_check


async def fire_cheques_check():
    cheques = await cheque_rq.get_all_cheques()
    for cheque in cheques:
        cheque_date = datetime.strptime(cheque.date, "%d-%m-%Y %H:%M:%S")
        if await half_year_check(cheque.date):
            if (datetime.now() - cheque_date) >= timedelta(days=14) and cheque.cheque_status == 'По чеку имеется отсрочка':
                await cheque_rq.set_status(cheque.id, 'Чек не оплачен по истечению 2-ух недель')
