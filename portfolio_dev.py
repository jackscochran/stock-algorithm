from sklearn.metrics import adjusted_mutual_info_score
from database import manager
from database.adaptors import portfolios as portfolio_adaptor

import pandas as pd


# ---------------------- RUNNER PROGRAM ---------------------- #

if __name__ == '__main__':
    manager.setup_connection()
    # load algorithm configurations #
    config = {
        "algorithm": "RandomForestRegressor-2",
        "start_date": "1996-08",
        "end_date": "2021-08",
        "holding_period": 3,
        "trade_load": 100,
        "trade_period": 3,  
        "lookback": 0,
        "short": False
    }

    # get portfolio data #
    adjustments = ['RandomForestRegressor-1', 'RandomForestRegressor-2', 'AlgoCLinReg-1', 'AlgoCLinReg-2']
    for adjustment in adjustments:
        print(f'\n----------------  RUN {adjustment} ----------------')
        # adjust desired config 
        config['algorithm'] = adjustment

        portfolio = portfolio_adaptor.get_portfolio(config)
        if portfolio is None:
            print('----------------  Loading Portfolio')

            trades=portfolio_adaptor.get_trades(config)

            print('----------------  Analyzing and Saving Portfolio')
            portfolio = portfolio_adaptor.add_portfolio(config, trades)

       

