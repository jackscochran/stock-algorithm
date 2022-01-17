from database import manager
from database.adaptors import portfolios as portfolio_adaptor

import pandas as pd


# ---------------------- RUNNER PROGRAM ---------------------- #

if __name__ == '__main__':
    manager.setup_connection()
    # load algorithm configurations #
    config = {
        "algorithm": "RandomForestRegressor-1",
        "start_date": "2014-01",
        "end_date": "2020-07",
        "holding_period": 12,
        "trade_load": 2,
        "trade_period": 1,  
        "lookback": 1
    }

    # get portfolio data #
    for i in range(1, 10):
        print(f'\n----------------  RUN {i} ----------------')
        # adjust desired config 
        config['trade_load'] = i

        portfolio = portfolio_adaptor.get_portfolio(config)
        if portfolio is None:
            print('----------------  Loading Portfolio')
            # data = pd.read_csv('portfolios.csv')
            # trades = portfolio_adaptor.load_portfolio(data, config)

            trades=portfolio_adaptor.get_trades(config)

            print('----------------  Analyzing and Saving Portfolio')
            portfolio = portfolio_adaptor.add_portfolio(config, trades)

       

