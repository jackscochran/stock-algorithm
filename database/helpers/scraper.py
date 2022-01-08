import yahoo_fin.stock_info as yf_stock_info
import math

def get_price(ticker, date):
    date = date + '-01'
    try:
        price = yf_stock_info.get_data(ticker, interval='1mo')['close'][date][0]
    except:
        price = math.nan
        
    return price

def get_monthly_prices(ticker):

    return yf_stock_info.get_data(ticker, interval='1mo')['close']

    
    

