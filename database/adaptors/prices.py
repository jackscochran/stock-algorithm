from ..data import prices
from ..helpers import scraper
from ..helpers import time
from ..helpers import mathematics as math_helper

import math
import random
import statistics

def get_monthly_price(ticker, date):

    if ticker is None:
        return None

    price = prices.MonthlyPrice.objects(ticker=ticker, date=date).first()

    if price is None: 
        price = add_monthly_price(ticker, date, scraper.get_price(ticker, date))

    if math.isnan(price.value):
        return None

    return price

def add_monthly_price(ticker, date, value):

    price = prices.MonthlyPrice.objects(ticker=ticker, date=date).first()

    if price is None:
        price = prices.MonthlyPrice(
            ticker = ticker,
            date = date,
            value = value
            )

        price.save()

    return price

def price_monthly_range(ticker, start, end):

    data = prices.MonthlyPrice.objects(
        ticker=ticker,
        date__gte=start,
        date__lte=end
    ).order_by('date')

    return data

def get_random_prices(date, n):
    samples = list(prices.MonthlyPrice.objects(date=date))   
    indices = []
    for i in range(n):
        indices.append(random.randint(0, len(samples) - 1))

    selection = []

    for index in indices:
        selection.append(samples[index])

    return selection

def get_avg_performance(ticker, date, period):

    start_price = get_monthly_price(ticker, date)
    end_price = get_monthly_price(ticker, time.get_months_ahead(date, period))

    if start_price is not None and end_price is not None:
        return math_helper.divide(end_price.value, start_price.value)

    return None

def get_performance(ticker, date, period):
    start_price = get_daily_price(ticker, date)
    end_price = get_daily_price(ticker, time.get_months_ahead(date, period))

    if start_price is None or end_price is None:
        return None

    return math_helper.divide(end_price.value, start_price.value)

def get_alpha(ticker, date, period, basline):
    stock_return = get_performance(ticker, date, period)
    baseline_return = get_performance(basline, date, period)

    if stock_return is None or baseline_return is None:
        return None

    return stock_return - baseline_return

def get_daily_price(ticker, date):

    if ticker is None:
        return None

    # get most recent price
    price = prices.DailyPrice.objects(ticker=ticker, date__lte=date).order_by('-date').first()

    return price

def add_daily_price(ticker, date, value):

    price = prices.DailyPrice.objects(ticker=ticker, date=date).first()

    if price is None:
        price = prices.DailyPrice(
            ticker = ticker,
            date = date,
            value = value
            )

        price.save()

    return price

def get_stock_sharpe_of_alpha(ticker, baseline, date, period, stdev_frquency):
    end_date =time.get_months_ahead(date, period)

    # calculate stdev
    returns = []
    current_date = date
    previous_price = None
    while current_date < end_date:
        current_price = get_daily_price(ticker, current_date)
        if current_price is not None:
            current_price = current_price.value
            if previous_price is not None:
                returns.append(math_helper.divide(current_price,previous_price))
            previous_price = current_price
        current_date = time.get_days_ahead(current_date,stdev_frquency)

    total_return = get_alpha(ticker, date, period, baseline)

    if len(returns) == 0 or total_return is None:
        return None

    return math_helper.divide(total_return, statistics.stdev(returns))