from database.adaptors import prices as price_adaptor
from database.adaptors import companies as company_adaptor
from database import manager
from helpers import scraper, time, fmp_adaptor
import math

manager.setup_connection()
tickers = fmp_adaptor.get_all_tickers_wth_financials()

count = 0
error_count = 0
min = 12088
total = len(tickers)

start_date = '1970-01'
end_date = '2011-01'

for ticker in tickers:
    print('\n----------')
    print(f'{ticker} -- {count} / {total}')
    print(f'Price data not avaialble: {error_count}')
    count+=1
    if count < min:
        continue
    
    if price_adaptor.get_monthly_price(ticker, start_date) is not None:
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
        
