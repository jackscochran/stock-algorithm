from datetime import datetime
from dateutil.relativedelta import relativedelta

def get_months_ahead(date, months):
    date_length = len(date)

    if date_length == 10:
        date_format = '%Y-%m-%d'
    elif date_length == 7:
        date_format = '%Y-%m'

    dtObj = datetime.strptime(date, date_format)

    return str(dtObj + relativedelta(months=months))[:date_length]

def get_days_ahead(date, days):
    date_format = '%Y-%m-%d'

    dtobj = datetime.strptime(date, date_format)

    return str(dtobj + relativedelta(days=days))[:10]
