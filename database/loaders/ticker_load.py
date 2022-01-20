from database import manager 
from helpers import fmp_adaptor
from database.adaptors import companies as company_adaptor

manager.setup_connection()
tickers = fmp_adaptor.get_all_tickers_wth_financials()
count = 0
min = 8796
for ticker in tickers:

    ticker = ticker.lower()
    count += 1
    print(f'{ticker} - {count} / {len(tickers)}')
    if count < min:
        continue

    company = company_adaptor.get_company(ticker)

    if company is None:

        profile = fmp_adaptor.get_profile(ticker)

        if profile is not None:
            company_adaptor.add_company(ticker, profile[0])