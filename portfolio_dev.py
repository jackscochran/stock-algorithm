from sklearn.metrics import adjusted_mutual_info_score
from database import manager
from database.adaptors import portfolios as portfolio_adaptor

import pandas as pd


# ---------------------- RUNNER PROGRAM ---------------------- #

if __name__ == '__main__':
    manager.setup_connection()
    # load algorithm configurations #
    config = {
        "algorithm": "AlgoCLinReg-14",
        "start_date": "1996-08",
        "end_date": "2021-11",
        "holding_period": 3,
        "trade_load": 50,
        "trade_period": 3,  
        "lookback": 0,
        "short": False
    }

    # get portfolio data #
    adjustments = ['RandomForestRegressor-14', 'RandomForestRegressor-15', 'RandomForestRegressor-16', 'RandomForestRegressor-17','AlgoCLinReg-14', 'AlgoCLinReg-15', 'AlgoCLinReg-17']
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

       

