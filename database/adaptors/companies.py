from ..data import companies

def get_company(ticker):
    return companies.Company.objects(ticker=ticker).first()

def add_company(ticker, profile):
    company = companies.Company(ticker=ticker, profile=profile)
    company.save()
    return company

def get_all_tickers():

    tickers = []
    for company in companies.Company.objects.all():
        tickers.append(company.ticker)

    return tickers