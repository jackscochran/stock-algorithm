from database import manager
from database.adaptors import portfolios as portfolio_adaptor

import pandas as pd

# portfolio configs to save to csv

config = {
    "algorithm": "RandomForestRegressor-21",
    "start_date": "1996-08",
    "end_date": "2021-08",
    "holding_period": 3,
    "trade_load": 500,
    "trade_period": 3,  
    "lookback": 0,
    "short": False
}

manager.setup_connection()

portfolio = portfolio_adaptor.get_portfolio(config)
returns = portfolio_adaptor.calculate_returns(portfolio.balances)

annual_returns = {}

for date in returns:
    year = date[:4]

    annual_returns[year] = annual_returns.get(year, 1) * returns[date]

pd.Series(annual_returns).to_csv(f'{config["algorithm"]}.csv')
