import requests

API_KEY = ''

def get_response(url):
    response = requests.get(url).json()

    if len(response)==0:
        return None

    return response

def get_all_tickers_wth_financials():
    api_url = f'https://fmpcloud.io/api/v3/financial-statement-symbol-lists?apikey={API_KEY}'
    return get_response(api_url)

def get_profile(ticker):
    api_url = f'https://fmpcloud.io/api/v3/profile/{ticker}?apikey={API_KEY}'
    return get_response(api_url)