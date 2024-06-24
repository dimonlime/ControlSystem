import asyncio
import json
import os
import re
from datetime import datetime, timedelta
from dateutil.parser import parse as parse_date
from openpyexcel import Workbook, load_workbook
from openpyexcel.styles import Font
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from odds.app.utils import control_system_departure, read_json

payments_purpose = [
    {'code': '4121', 'name': 'поставщикам за сырье, материалы, работы услуги - всего'},
    {'code': '41211', 'name': 'поставщику ФФ'},
    {'code': '41212', 'name': 'поставщику Фабрика'},
    {'code': '41213', 'name': 'Прочие подрядчики'},
    {'code': '4122', 'name': 'в связи с оплатой труда работников'},
    {'code': '4123', 'name': 'в связи с оплатой кредитных обязательств (тело кредита + проценты)'},
    {'code': '4128', 'name': 'иных налогов и сборов'},
    {'code': '4129', 'name': 'прочие платежи'}
]

payments_full = [{'code': '4120', 'name': 'Платежи - всего'}]
income_full = [{'code': '4110', 'name': 'Поступления - всего'}]
income_purpose = [{'code': '4111', 'name': 'от продажи продукции,товаров,услуг По Основному ОКВЭД'},
                  {'code': '4119', 'name': 'прочие поступления'}]
cash_flow = [{'code': '4100', 'name': 'Сальдо денежных потоков от текущих операций'}]


def parse_payments(responsePay, payments_purpose):
    payments = []
    date_now = datetime.now()
    for item in responsePay:
        payment_purpose = item['paymentPurpose']
        for payment in payments_purpose:
            pattern = fr'\b{re.escape(payment["code"])}\b'
            if re.search(pattern, payment_purpose):
                date = item['created']
                amount = item['amount']
                date_obj = parse_date(date)
                if is_date_in_current_month(date_now, date_obj):
                    payments.append({'code': payment['code'], 'name': payment['name'], 'amount': amount, 'date': date})
    return payments


def total_received_incomes(incomes):
    total_received_income = []
    total_received_wb = 0
    total_received_other = 0
    date_now = datetime.now().date()
    start_date, end_date = get_start_and_end_of_current_month(date_now)
    for item in incomes:
        print(item)
        if item['code'] == '4111':
            print(item)
            total_received_wb += item['amount']
        elif item['code'] == '4119':
            total_received_other += item['amount']
    total_received_income.append(
        {'code': '4111', 'name': 'от продажи продукции,товаров,услуг По Основному ОКВЭД', 'amount': total_received_wb,
         'date': f"{start_date} - {end_date}"})
    total_received_income.append({'code': '4119', 'name': 'прочие поступления', 'amount': total_received_other,
                                  'date': f"{start_date} - {end_date}"})
    return total_received_income


def total_executed_payments(payments):
    total_executed_payments = []
    amount_supplier_for_material = 0
    amount_supplier_ff = 0
    amount_supplier_fabric = 0
    amount_supplier_other = 0
    amount_employess_paid = 0
    amount_credits = 0
    amount_taxes = 0
    amount_other_payments = 0
    date_now = datetime.now().date()
    start_date, end_date = get_start_and_end_of_current_month(date_now)
    for item in payments:
        if item['code'] == '4121':
            amount_supplier_for_material += item['amount']
        elif item['code'] == '41211':
            amount_supplier_ff += item['amount']
        elif item['code'] == '41212':
            amount_supplier_fabric += item['amount']
        elif item['code'] == '41213':
            amount_supplier_other += item['amount']
        elif item['code'] == '4122':
            amount_employess_paid += item['amount']
        elif item['code'] == '4123':
            amount_credits += item['amount']
        elif item['code'] == '4128':
            amount_taxes += item['amount']
        elif item['code'] == '4129':
            amount_other_payments += item['amount']
    total_executed_payments.append({'code': '4121', 'name': 'поставщикам за сырье, материалы, работы услуги - всего',
                                    'amount': amount_supplier_for_material, 'date': f"{start_date} - {end_date}"})
    total_executed_payments.append(
        {'code': '41211', 'name': 'поставщику ФФ', 'amount': amount_supplier_ff, 'date': f"{start_date} - {end_date}"})
    total_executed_payments.append({'code': '41213', 'name': 'Прочие подрядчики', 'amount': amount_supplier_other,
                                    'date': f"{start_date} - {end_date}"})
    total_executed_payments.append(
        {'code': '4122', 'name': 'в связи с оплатой труда работников', 'amount': amount_employess_paid,
         'date': f"{start_date} - {end_date}"})
    total_executed_payments.append(
        {'code': '4123', 'name': 'в связи с оплатой кредитных обязательств (тело кредита + проценты)',
         'amount': amount_credits, 'date': f"{start_date} - {end_date}"})
    total_executed_payments.append(
        {'code': '4128', 'name': 'иных налогов и сборов', 'amount': amount_taxes, 'date': f"{start_date} - {end_date}"})
    total_executed_payments.append({'code': '4129', 'name': 'прочие платежи', 'amount': amount_other_payments,
                                    'date': f"{start_date} - {end_date}"})
    return total_executed_payments


def full_amount(payments, payments_full):
    full_amount = []
    total_amount = 0
    date_now = datetime.now().date()
    start_date, end_date = get_start_and_end_of_current_month(date_now)
    for payment in payments:
        total_amount += payment['amount']
    full_amount.append({'code': payments_full[0]['code'], 'name': payments_full[0]['name'], 'amount': total_amount,
                        'date': f"{start_date} - {end_date}"})
    return full_amount


def cash_flow_balance(full_payment, full_income, cash_flow):
    cash_flow_balance = []
    total_cash_flow = full_income[0]['amount'] - full_payment[0]['amount']
    date_now = datetime.now().date()
    start_date, end_date = get_start_and_end_of_current_month(date_now)
    cash_flow_balance.append({'code': cash_flow[0]['code'], 'name': cash_flow[0]['name'], 'amount': total_cash_flow,
                              'date': f"{start_date} - {end_date}"})
    return cash_flow_balance


def parse_incomes(responsePay, incomes_purpose):
    incomes = []
    date_now = datetime.now()
    for item in responsePay:
        contragent_name = item['contragentName']
        status = item['status']
        for income in incomes_purpose:
            code = income['code']
            amount = item['amount']
            date = item['created']
            purpose = income['name']
            date_object = parse_date(date)

            if is_date_in_current_month(date_now, date_object):
                if (('Вайлдберриз' in contragent_name) or ('ВАЙЛДБЕРРИЗ' in contragent_name)) and (
                        status == "Received") and code == '4111':
                    incomes.append({'code': code, 'name': purpose, 'amount': amount, 'date': date})
                elif (('Вайлдберриз' not in contragent_name) and (
                        'ВАЙЛДБЕРРИЗ' not in contragent_name)) and status == "Received" and code == '4119':
                    incomes.append({'code': code, 'name': purpose, 'amount': amount, 'date': date})
    return incomes


def is_date_in_current_month(current_date, other_date):
    return current_date.year == other_date.year and current_date.month == other_date.month


def get_start_and_end_of_current_month(current_date):
    start_of_month = current_date.replace(day=1)

    if current_date.month == 12:
        end_of_month = current_date.replace(year=current_date.year + 1, month=1, day=1) - timedelta(days=1)
    else:
        end_of_month = current_date.replace(month=current_date.month + 1, day=1) - timedelta(days=1)
    return start_of_month, end_of_month


def add_to_db_payments_incomes(records, model_class, session):
    for record in records:
        existing_record = session.query(model_class).filter_by(
            code=record['code'],
            date=record['date'],
            name=record['name'],
        ).first()

        if existing_record:
            existing_record.amount = record['amount']
        else:
            new_record = model_class(**record)
            session.add(new_record)

    session.commit()


def frame_report_ODDS(full_payments, full_income, total_received, total_executed_pay, full_cash_flow_balance,
                      excel=r"odds\excel_files\report_ODDS.xlsx"):
    wb = Workbook()
    ws = wb.active
    date_now = datetime.now().date()
    start_date, end_date = get_start_and_end_of_current_month(date_now)
    ws.title = 'Отчет'
    ws['A1'] = 'Наименование показателя'
    ws['B1'] = 'Код'
    ws['C1'] = f"За {start_date} - {end_date}"
    ws['A2'] = 'Денежные потоки от текущих операция'
    ws['A2'].font = Font(bold=True)
    ws.merge_cells('A2:C2')
    ws['A3'] = full_income[0]['name']
    ws['B3'] = full_income[0]['code']
    ws['C3'] = full_income[0]['amount']
    ws['A3'].font = Font(bold=True)
    row = 4
    for item in total_received:
        name = item['name']
        code = item['code']
        amount = item['amount']
        ws[f"A{row}"] = name
        ws[f"B{row}"] = code
        ws[f"C{row}"] = amount
        row += 1

    ws[f"A{row}"] = full_payments[0]['name']
    ws[f"B{row}"] = full_payments[0]['code']
    ws[f"C{row}"] = full_payments[0]['amount']
    ws[f'A{row}'].font = Font(bold=True)
    row += 1
    for item in total_executed_pay:
        name = item['name']
        code = item['code']
        amount = item['amount']
        ws[f"A{row}"] = name
        ws[f"B{row}"] = code
        ws[f"C{row}"] = amount
        row += 1
    ws[f"A{row}"] = full_cash_flow_balance[0]['name']
    ws[f"B{row}"] = full_cash_flow_balance[0]['code']
    ws[f"C{row}"] = full_cash_flow_balance[0]['amount']
    ws.column_dimensions['A'].width = 65
    ws.column_dimensions['B'].width = 7
    ws.column_dimensions['C'].width = 25
    wb.save(excel)


def frame_2(pay_fullfulment, pay_logistic, excel=r"odds\excel_files\report_ODDS.xlsx"):
    try:
        wb = load_workbook(excel)
    except FileNotFoundError:
        wb = Workbook()

    if 'Payments' in wb.sheetnames:
        ws = wb['Payments']
    else:
        ws = wb.create_sheet('Payments')

    ws.delete_rows(1, ws.max_row)

    ws['A1'] = 'Наименование показателя'
    ws['B1'] = 'Сумма'
    ws['A2'] = 'Платежи'
    ws['A2'].font = Font(bold=True)
    ws.merge_cells('A2:C2')
    ws['A3'] = 'Заплатить фф (Руб)'
    ws['B3'] = pay_fullfulment
    ws['A4'] = 'Заплатить логистам ($)'
    ws['B4'] = pay_logistic

    wb.save(excel)


def get_buyouts(data_analit_wb):
    buyouts = []
    buyouts_count_full = 0
    buyouts_sum_full = 0
    for item in data_analit_wb['data']['cards']:
        article = item['vendorCode']
        buyouts_count = item['statistics']['selectedPeriod']['buyoutsCount']
        buyouts_count_full += buyouts_count
        buyouts_sum_rub = item['statistics']['selectedPeriod']['buyoutsSumRub']
        buyouts_sum_full += buyouts_sum_rub
        buyouts.append({"article": article, "buyouts_count": buyouts_count, "buyouts_sum_rub": buyouts_sum_rub})
    return buyouts, buyouts_count_full, buyouts_sum_full


def get_departure_full(departure_with_sizes):
    departure_full = []
    count_departure_full = 0
    for item in departure_with_sizes:
        article = item['article']
        count_departure = item['S'] + item['M'] + item['L']
        count_departure_full += count_departure
        departure_full.append({"article": article, "count_departure": count_departure})
    return departure_full, count_departure_full


def get_pay_fullfilment(departure):
    config = read_json('odds/config/config.json')
    return departure * config['fullfilment']


def get_pay_logistic(departure):
    config = read_json('odds/config/config.json')
    return departure * config['product_weight'] * config['logistics']


def initial():
    from odds.app.Request import res_pay, response_analit
    from odds.models.models import Base, Payment, Income
    engine = create_engine('sqlite:///db1.sqlite3')
    Session = sessionmaker(bind=engine)
    session = Session()
    response = res_pay
    responsePay = response.json()
    parsed_payments = parse_payments(responsePay, payments_purpose)
    parsed_incomes = parse_incomes(responsePay, income_purpose)
    full_payment = full_amount(parsed_payments, payments_full)
    print(full_payment)
    full_income = full_amount(parsed_incomes, income_full)
    total_received = total_received_incomes(parsed_incomes)
    total_executed_pay = total_executed_payments(parsed_payments)
    full_cash_flow_balance = cash_flow_balance(full_payment, full_income, cash_flow)

    add_to_db_payments_incomes(full_payment, Payment, session)
    add_to_db_payments_incomes(total_executed_pay, Payment, session)
    add_to_db_payments_incomes(full_cash_flow_balance, Payment, session)

    add_to_db_payments_incomes(full_income, Income, session)
    add_to_db_payments_incomes(total_received, Income, session)

    session.close()
    frame_report_ODDS(full_payment, full_income, total_received, total_executed_pay, full_cash_flow_balance)

    print(parsed_payments)
    print('---------------------')
    print(parsed_incomes)
    print('---------------------')
    print(full_payment)
    print('---------------------')
    buyouts, buyouts_count_full, buyouts_sum_full = get_buyouts(response_analit.json())
    print(buyouts)
    print('---------------------')
    departure_with_sizes = control_system_departure()
    departure_full, count_departure = get_departure_full(departure_with_sizes)
    print(departure_full)
    print(count_departure)
    print('---------------------')
    pay_fullfilment = get_pay_fullfilment(count_departure)
    pay_logistic = get_pay_logistic(count_departure)
    print(get_pay_fullfilment(count_departure))
    print(get_pay_logistic(count_departure))
    frame_2(pay_fullfilment, pay_logistic)
