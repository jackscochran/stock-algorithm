from ..data import prices
import math
from ..helpers import scraper
from ..helpers import time
from ..helpers import mathematics as math_helper
import random

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

def get_random_prices(date, n):
    samples = list(prices.MonthlyPrice.objects(date=date))   
    indices = []
    for i in range(n):
        indices.append(random.randint(0, len(samples) - 1))

    selection = []

    for index in indices:
        selection.append(samples[index])

    return selection

def get_performance(ticker, date, holding_period):
    start_price = get_monthly_price(ticker, date)
    end_price = get_monthly_price(ticker, time.get_months_ahead(date, holding_period))

    if start_price is not None and end_price is not None:
        return math_helper.divide(end_price.value, start_price.value)

    return None