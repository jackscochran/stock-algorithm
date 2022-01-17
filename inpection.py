import numpy as np

from helpers import visualization as viz
from helpers import time
from database import manager
from database.adaptors import prices as price_adaptor

def monthly_price_correlation():
    n = 6000
    current_date = '2021-12'
    lag = 12
    
    x = []
    y = []
    for current_price in price_adaptor.get_random_prices(current_date, n):
        prev_price = price_adaptor.get_monthly_price(current_price.ticker, time.get_months_ahead(current_price.date, -lag))
        if prev_price is not None:
            x.append(prev_price.value)
            y.append(current_price.value)

    viz.scatter(x, y)



if __name__ == '__main__':
    manager.setup_connection()
    monthly_price_correlation()