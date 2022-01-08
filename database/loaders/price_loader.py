from database.adaptors import prices as price_adaptor
from database.adaptors import companies as company_adaptor
from database import manager
from helpers import scraper, time
import math

manager.setup_connection()
tickers = ['spy'] #company_adaptor.get_all_tickers()

count = 0
error_count = 0
min = 0
total = len(tickers)

start_date = '2011-01'
end_date = '2021-12'

for ticker in tickers:
    print('\n----------')
    print(f'{ticker} -- {count} / {total}')
    print(f'Price data not avaialble: {error_count}')
    count+=1
    if count < min:
        continue
    
    prices = scraper.get_monthly_prices(ticker)
    if prices is None:
        error_count += 1
        continue

    current_date = start_date
    while current_date <= end_date:
        date = current_date + '-01'
        
        try:
            price = prices[date]
        except:
            price = math.nan

        price_adaptor.add_monthly_price(ticker, current_date, price)
        current_date = time.get_months_ahead(current_date, 1)
        
