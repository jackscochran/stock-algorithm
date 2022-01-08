from helpers import time
from database.helpers import mathematics as math_helper
import pandas as pd
import queue
from database.adaptors import prices as price_adaptor
from database.adaptors import portfolios as portfolio_adaptor
from database.adaptors import evaluators as evaluator_adaptor
from database.adaptors import evaluations as evaluation_adaptor
import math
import random


def get_trades(config):

    trades = {}
    current_date = config['start_date']
    while(current_date < config['end_date']):
        trades[current_date] = evaluation_adaptor.create_portfolio(current_date, config['trade_load'], evaluator_adaptor.get_key(config))
        current_date = time.get_months_ahead(current_date, config['trade_period'])

    return trades

def get_random_trade_portfolios(n, start_date, end_date, period, load):

    trade_portfolios = [{} for i in range(n)]

    current_date = start_date
    while(current_date <= end_date):
        print(f'Getting trades for {current_date}')
        random_tickers = [price.ticker for price in price_adaptor.get_random_prices(current_date, n*load)]
        random.shuffle(random_tickers)
        
        for portfolio in trade_portfolios:
            portfolio[current_date] = []

        for i in range(len(random_tickers)):
            trade_portfolios[int(i/load)][current_date].append(random_tickers[i])

        # go to next time step
        current_date = time.get_months_ahead(current_date, period)

    return trade_portfolios

def trade_returns(trades, period, portfolio_size, csv_name=None):


    # if len(trades) % period != 0:
    #     raise ValueError('Length of trades dict must be divisble by the period')

    # initialize csv df
    if csv_name:
        df = {
            'date': [],
            'ticker': [],
            'balance': [],
            'previous_price':[],
            'return': [],
            'weighted': [],
            'asset_index': []
        }
    
    portfolio_size = int(portfolio_size)

    # initialize balance and portfolio
    total_balance = 1
    portfolio = queue.Queue(maxsize=portfolio_size)
    asset_index = 0
    monthly_balances = {}

    # keep track of outlier
    outlier_definition = 5
    outlier_count = 0

    # initalize empty portfolio
    while not portfolio.full():
        portfolio.put({
            'ticker': None,
            'balance': total_balance / portfolio_size,
            'previous_price': None,
            'return': 1,
            'asset_index': asset_index
        })

        asset_index = (asset_index + 1) % portfolio_size

    # get time range
    start_date = list(trades.keys())[0]
    end_date = list(trades.keys())[-1:][0]
    current_date = start_date

    while current_date <= end_date:

        # get portfolio returns from last period, update balance, and get new total balance
        total_balance = 0
        total_returns = 0
        for i in range(portfolio_size):
            # iterate through portfolio
            asset = portfolio.get()
            portfolio.put(asset)

            if asset['ticker'] is not None: # investment made
                current_price = price_adaptor.get_monthly_price(asset['ticker'], current_date)
                if current_price is None:
                    current_price = asset['previous_price']
                else:
                    current_price = current_price.value

                if asset['previous_price'] is not None: # if not first period of holding
                    asset['return'] = current_price / asset['previous_price']

                    # check for outliers
                    if asset['return'] > outlier_definition:
                        outlier_count += 1

                asset['previous_price'] = current_price # save price
                asset['balance'] *= asset['return'] # calculate new balance


            total_returns += asset['return']
            total_balance += asset['balance']

        # save to csv dict
        if csv_name:
            for i in range(portfolio_size):
                asset = portfolio.get()
                portfolio.put(asset)
                df['ticker'].append(asset['ticker'])
                df['date'].append(current_date)
                df['balance'].append(asset['balance'])
                df['previous_price'].append(asset['previous_price'])
                df['return'].append(asset['return'])
                df['weighted'].append(0)
                df['asset_index'].append(asset['asset_index'])
        
        # log results
        # print('\n------------')
        # print(current_date)
        # print(f'Average return: {total_returns/portfolio_size}')
        # print(f'Total Balance: {total_balance}')

        # save data to return variable
        monthly_balances[current_date] = total_balance
           

        # check if any trades are made on current date
        if current_date not in trades.keys(): # no trades make
            current_date = time.get_months_ahead(current_date, period)
            continue

        # make trades and redistribute

        next_redistribution = 0
        available_accounts = set([i for i in range(portfolio_size)])

        for ticker in trades[current_date]:

            sell_balance = portfolio.get()['balance']
            # add company to portfolio
            price = price_adaptor.get_monthly_price(ticker, current_date)
            if price is not None:
                price = price.value

            portfolio.put({
                'ticker': ticker,
                'balance': total_balance / portfolio_size,
                'previous_price': price,
                'return': 1,
                'asset_index': asset_index
            })

            
            # loop until no liaiblities, ensuring no balances go negative
            next_redistribution += sell_balance - total_balance / portfolio_size
            available_accounts.remove(asset_index)
            asset_index = (asset_index + 1) % portfolio_size

        while(True):
            
            current_redistribution = next_redistribution
            next_redistribution = 0
            asset_redistribution = math_helper.divide(current_redistribution, len(available_accounts))

            for i in range(portfolio_size):
                asset = portfolio.get()

                if asset['asset_index'] not in available_accounts:
                    portfolio.put(asset)
                    continue # account is empty or was just invested

                if asset['balance'] + asset_redistribution < 0: # cant pay redistribution
                    available_accounts.remove(asset['asset_index'])
                    next_redistribution += asset['balance'] + asset_redistribution

                asset['balance'] = max(0, asset['balance'] + asset_redistribution)

                portfolio.put(asset)

            if math.isclose(next_redistribution, 0):
                break


        # save to csv dict
        if csv_name:
            for i in range(portfolio_size):
                asset = portfolio.get()
                portfolio.put(asset)
                df['ticker'].append(asset['ticker'])
                df['date'].append(current_date)
                df['balance'].append(asset['balance'])
                df['previous_price'].append(asset['previous_price'])
                df['return'].append(asset['return'])
                df['weighted'].append(1)
                df['asset_index'].append(asset['asset_index'])


        # go to next date
        current_date = time.get_months_ahead(current_date, period)

    # log outlier counts
    # print(f'Number of monthly returns above {outlier_definition}: {outlier_count}')

    if csv_name:
        pd.DataFrame.from_dict(df).to_csv(f'returns/{csv_name}.csv')

    return monthly_balances

def simulate(n, config):

    # see how many simulations have been run to date and adjust n
    simulations = portfolio_adaptor.get_simulations(config)
    n -= len(simulations)
    
    if n > 0: # must generate more simulations
        generate_simulations(n, config)
        simulations = portfolio_adaptor.get_simulations(config)

    return simulations
    
    
def generate_simulations(n, config):
    # get n random portfolios
    trade_portfolios = get_random_trade_portfolios(
        n, 
        config['start_date'], 
        config['end_date'], 
        config['trade_period'], 
        config['trade_load' ])

    count = 0
    portfolio_size = config['trade_load'] * config['holding_period'] / config['trade_period']

    for trades in trade_portfolios:
        print(f'Running simulation {count} / {n}')
        count+=1

        # get balances
        balances = trade_returns(trades, config['trade_period'], portfolio_size)

        # save simulation
        portfolio_adaptor.add_portfolio(
            f'Simulation-{config["trade_period"]}x{config["trade_load"]}x{config["holding_period"]}',
            config['start_date'],
            config['end_date'],
            trades,
            balances
            )
