from ..data import portfolios
from ..helpers import mathematics as math_helper
from ..helpers import time
from ..adaptors import prices as price_adaptor
from ..adaptors import evaluations as evaluation_adaptor
from ..adaptors import companies as company_adaptor
from .. import manager

import statistics
import math
import queue
import random

import pandas as pd

def get_portfolio(config):

    portfolio = portfolios.Portfolio.objects(
        algorithm = config['algorithm'],    
        start_date= config['start_date'],
        end_date= config['end_date'],
        holding_period= config['holding_period'],
        trade_load= config['trade_load'],
        trade_period= config['trade_period'],
        lookback= config['lookback'],
        short=config['short']
    )

    if portfolio is None:
        return portfolio

    return portfolio.first()

def get_versions(config, uniform_figs):
    
    versions = portfolios.Portfolio.objects(
        start_date = config['start_date'],
        end_date = config['end_date'],
        algorithm__contains = 'Reg'
    ).order_by(uniform_figs[0])
    filtered = dict()

    for version in versions:
        version_config = {
            "algorithm": version.algorithm,
            "holding_period": version.holding_period,
            "trade_load": version.trade_load,
            "trade_period": version.trade_period,
            "lookback": version.lookback,
            "short": version.short
        }

        # check if version should be added 
        clear = True
        for fig in version_config:
            if fig in uniform_figs and config[fig] != version_config[fig]:
                clear = False # spec config is uniform in version selection but does not match
        if not clear:
            continue
        
        filtered[ # format version config key string that can be displayed on graph
            '-'.join([str(version_config[fig]) for fig in list(set(list(config.keys()))-set(uniform_figs))])
        ] = version

            
    return filtered

def sp500_balances(start_date, end_date, period):
    balances = {}
    current_date = start_date
    previous_date = None
    while current_date <= end_date:
        
        if previous_date is None:
            balances[current_date] = 1
        else:
            performance = price_adaptor.get_avg_performance('spy', current_date, -period)
            if performance is None:
                performance = 1
            balances[current_date] = balances[previous_date] / performance

        previous_date = current_date
        current_date = time.get_months_ahead(current_date, period)

    return balances


def load_portfolio(data, config):

    manager.setup_connection()

    size = config['trade_load']
    portfolio = {}

    current_date = None

    for row in data.iterrows():
        row = row[1]

        # start of new month
        if current_date != row['date']:

            if current_date is not None:
                while len(portfolio[current_date]) < size:
                    portfolio[current_date].append(None)

            current_date = row['date']
            portfolio[row['date']] = []

        elif len(portfolio[row['date']]) >= size:
            continue

        price = price_adaptor.get_monthly_price(row['ticker'], row['date'])

        if price is not None:
            portfolio[row['date']].append(row['ticker'])

    return portfolio

def add_portfolio(config, trades):
    csv_name = config['algorithm']
    balances = calculate_balances(trades, config, csv_name=csv_name)
    metrics = calculate_metrics(balances, calculate_returns(sp500_balances(config['start_date'],config['end_date'], config['trade_period'])))

    portfolio = portfolios.Portfolio(
        algorithm = config['algorithm'],
        start_date= config['start_date'],
        end_date= config['end_date'],
        holding_period= config['holding_period'],
        trade_load= config['trade_load'],
        trade_period= config['trade_period'],
        lookback= config['lookback'],
        trades= trades,
        balances= balances,
        metrics = metrics
        )

    if 'short' in config.keys():
        portfolio.short = config['short']

    portfolio.save()
    return portfolio


def get_trades(config):
    
    trades = {}
    current_date = config['start_date']
    while(current_date <= config['end_date']):
        trades[current_date] = evaluation_adaptor.create_portfolio(current_date, config['trade_load'], config['algorithm'], config['lookback'], config['short'])
        current_date = time.get_months_ahead(current_date, config['trade_period'])

    return trades

def calculate_balances(trades, config, csv_name=None):
    # initialize csv df
    if csv_name:
        df = {
            'date': [],
            'ticker': [],
            'sector': [],
            'industry': [],
            'balance': [],
            'previous_price':[],
            'return': [],
            'weighted': [],
            'asset_index': []
        }
    
    portfolio_size = int(config['trade_load'] * config['holding_period'] / config['trade_period'])

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

                company = company_adaptor.get_company(asset['ticker'])
                if company is None:
                    df['sector'].append(None)
                    df['industry'].append(None)
                else:
                    df['sector'].append(company.profile['sector'])
                    df['industry'].append(company.profile['industry'])

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
        if current_date not in trades.keys() or trades[current_date] is None: # no trades make
            current_date = time.get_months_ahead(current_date, config['holding_period'])
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

            
            next_redistribution += sell_balance - total_balance / portfolio_size
            available_accounts.remove(asset_index)
            asset_index = (asset_index + 1) % portfolio_size

        for i in range(portfolio_size):
            # iterate through portfolio
            asset = portfolio.get()
            asset['balance'] = total_balance / portfolio_size
            portfolio.put(asset)

        # while(True):
            
        #     current_redistribution = next_redistribution
        #     next_redistribution = 0
        #     asset_redistribution = math_helper.divide(current_redistribution, len(available_accounts))

        #     for i in range(portfolio_size):
        #         asset = portfolio.get()

        #         if asset['asset_index'] not in available_accounts:
        #             portfolio.put(asset)
        #             continue # account is empty or was just invested

        #         if asset['balance'] + asset_redistribution < 0: # cant pay redistribution
        #             available_accounts.remove(asset['asset_index'])
        #             next_redistribution += asset['balance'] + asset_redistribution

        #         asset['balance'] = max(0, asset['balance'] + asset_redistribution)

        #         portfolio.put(asset)

        #     if math.isclose(next_redistribution, 0):
        #         break


        # save to csv dict
        if csv_name:
            for i in range(portfolio_size):
                asset = portfolio.get()
                portfolio.put(asset)

                company = company_adaptor.get_company(asset['ticker'])
                if company is None:
                    df['sector'].append(None)
                    df['industry'].append(None)
                else:
                    df['sector'].append(company.profile['sector'])
                    df['industry'].append(company.profile['industry'])

                df['ticker'].append(asset['ticker'])
                df['date'].append(current_date)
                df['balance'].append(asset['balance'])
                df['previous_price'].append(asset['previous_price'])
                df['return'].append(asset['return'])
                df['weighted'].append(1)
                df['asset_index'].append(asset['asset_index'])


        # go to next date
        current_date = time.get_months_ahead(current_date, config['trade_period'])

    # log outlier counts
    # print(f'Number of monthly returns above {outlier_definition}: {outlier_count}')

    if csv_name:
        pd.DataFrame.from_dict(df).to_csv(f'returns/{csv_name}.csv')

    return monthly_balances

def calculate_returns(balances):
    returns = dict()
    prev_bal = 1
    for date in balances:
        returns[date] = balances[date] / prev_bal
        prev_bal = balances[date]

    return returns

def calculate_alpha(returns, baseline):
    alpha = dict()

    for date in returns:
        alpha[date] = returns[date] - baseline[date]

    return alpha

def calculate_metrics(balances, baseline):

    # get monthly and annual returns
    periodic_returns = []
    annual_returns = []

    # track squared downside
    annual_downside = []
    periodic_downside = []

    # track trailing balance to get return
    previous_periodic_price = 1
    previous_annual_balance = 1

    # keep track of year
    previous_year = None

    for date in balances:

        if date[:4] != previous_year: # check if month is end of year
            if previous_year is not None:
                annual_returns.append(previous_periodic_price / previous_annual_balance - 1)
                previous_annual_balance = previous_periodic_price

            previous_year = date[:4]

        periodic_returns.append(balances[date] / previous_periodic_price - 1)
        previous_periodic_price = balances[date]

    # add final annual return
    annual_returns.append(previous_periodic_price / previous_annual_balance - 1)

    # get downsides
    for gain in periodic_returns:
        if gain < 0:
            periodic_downside.append(gain*gain) 
        else:
            periodic_downside.append(0)

    periodic_downside = math.sqrt(sum(periodic_downside)/len(periodic_downside))

    for gain in annual_returns:
        if gain < 0:
            annual_downside.append(gain*gain) 
        else:
            annual_downside.append(0)

    annual_downside = math.sqrt(sum(annual_downside)/len(annual_downside))


    periodic_alpha = calculate_alpha(
        calculate_returns(balances),
        calculate_returns(baseline)
    )

    metrics = {}

    metrics['final_balance'] = previous_periodic_price
    metrics['average_annual_returns'] = statistics.mean(annual_returns)
    metrics['average_periodic_returns'] = statistics.mean(periodic_returns)
    metrics['median_annual_return'] = statistics.median(annual_returns)
    metrics['median_periodic_returns'] = statistics.median(periodic_returns)
    metrics['annual_stdev'] = statistics.stdev(annual_returns)
    metrics['periodic_stdev'] = statistics.stdev(periodic_returns)
    metrics['periodic_sharpe'] = math_helper.divide(metrics['average_periodic_returns'], metrics['periodic_stdev'])
    metrics['annual_sharpe'] = math_helper.divide(metrics['average_annual_returns'], metrics['annual_stdev'])
    metrics['periodic_downside'] = periodic_downside
    metrics['annual_downside'] = annual_downside
    metrics['periodic_sortino'] = math_helper.divide(metrics['average_periodic_returns'], metrics['periodic_downside'])
    metrics['annual_sortino'] = math_helper.divide(metrics['average_annual_returns'], metrics['annual_downside'])
    metrics['mean_periodic_alpha'] = statistics.mean(list(periodic_alpha.values()))
    metrics['CAGR'] = metrics['final_balance']**(1/len(annual_returns)) - 1
    metrics['max_annual_downside'] = min(annual_returns)
    metrics['max_periodic_downside'] = min(periodic_returns)
    metrics['value_at_risk_95%'] = metrics['average_annual_returns'] - 1.65 * metrics['annual_stdev']
    metrics['value_at_risk_99%'] = metrics['average_annual_returns'] - 2.33 * metrics['annual_stdev']
    
    return metrics

def update_metrics():
    for portfolio in portfolios.Portfolio.objects.all():
        portfolio.metrics = calculate_metrics(portfolio.balances, calculate_returns(sp500_balances(portfolio.start_date, portfolio.end_date,  portfolio.trade_period)))
        portfolio.save()


def get_simulations(config):
    return portfolios.Portfolio.objects(
        algorithm__startswith = 'RandomSelection',
        start_date= config['start_date'],
        end_date= config['end_date'],
        holding_period= config['holding_period'],
        trade_load= config['trade_load'],
        trade_period= config['trade_period'],
        )

def get_random_trade_portfolios(n, config):

    trade_portfolios = [{} for i in range(n)]

    current_date = config['start_date']
    while(current_date <= config['end_date']):
        print(f'Getting trades for {current_date}')
        tickers = [
            eval.ticker for eval in evaluation_adaptor.get_evaluations(config['algorithm'], current_date, current_date)
            ]
        
        for portfolio in trade_portfolios:
            portfolio[current_date] = []
            for ticker in random.choices(tickers, k=int(config['trade_load'])):
                portfolio[current_date].append(ticker)

        # go to next time step
        current_date = time.get_months_ahead(current_date, config['trade_period'])

    return trade_portfolios

def simulate(n, config):
    simulations = get_simulations(config)
    
    if len(simulations) < n:
        trade_portfolios = get_random_trade_portfolios(n-len(simulations), config)
        
        count = 0
        for trades in trade_portfolios:
            count+=1
            print(f'Saving Portfolios {len(simulations) + count} / {n}')

            config['algorithm'] = f'RandomSelection-{len(simulations) + count}'
            add_portfolio(config, trades)

    return get_simulations(config)

def simulation_statistics(portfolio, n):

    # initalize simulation dict
    simulated_metrics = dict()
    probablities = dict()
    for metric in portfolio.metrics:
        simulated_metrics[metric] = []
        probablities[metric] = 0

    # get simulations
    simulations = simulate(
        n,
        {
        "algorithm": portfolio.algorithm,
        "start_date": portfolio.start_date,
        "end_date": portfolio.end_date,
        "holding_period": portfolio.holding_period,
        "trade_load": portfolio.trade_load,
        "trade_period": portfolio.trade_period,  
        "lookback": portfolio.lookback
    })

    # save metrics for each simulation
    for simulation in simulations:
        for metric in simulation.metrics:
            simulated_metrics[metric].append(simulation.metrics[metric])

            # track probablity
            if simulation.metrics[metric] > portfolio.metrics[metric]:
                probablities[metric] += 1

    
    # get statistics
    stats = dict()

    for metric in simulated_metrics:
        stats[metric] = dict()

        # save portfolio value
        stats[metric]['portfolio'] = portfolio.metrics[metric]

        # get metric descriptive statistics
        stats[metric]['runs'] = len(simulations)
        stats[metric]['mean'] = statistics.mean(simulated_metrics[metric])
        stats[metric]['median'] = statistics.median(simulated_metrics[metric])
        stats[metric]['stdev'] = statistics.stdev(simulated_metrics[metric])
        stats[metric]['max'] = max(simulated_metrics[metric])
        stats[metric]['min'] = min(simulated_metrics[metric])

        # get metric probablity
        stats[metric]['significance'] = math_helper.divide(probablities[metric], len(simulations))

    return stats

def get_simulation_returns(config):

    returns = {}
    for simulation in get_simulations(config):
        simulation_returns = calculate_returns(simulation.balances)
        for date in simulation_returns:
            if date not in returns.keys():
                returns[date] = []
            returns[date].append(simulation_returns[date])

    return returns