from pymongo.compression_support import SnappyContext
from ..data import portfolios
from ..helpers import mathematics as math_helper
from ..helpers import time
from ..adaptors import prices as price_adaptor
from .. import manager
import statistics
import math
import pandas as pd

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

            print(row['date'])
            current_date = row['date']
            portfolio[row['date']] = []

        elif len(portfolio[row['date']]) >= size:
            continue

        price = price_adaptor.get_monthly_price(row['ticker'], row['date'])

        if price is not None:
            print(row['ticker'])
            portfolio[row['date']].append(row['ticker'])

    return portfolio

def add_portfolio(creator, start_date, end_date, trades, balances):

    metrics = calculate_metrics(balances)

    portfolio = portfolios.Portfolio(
        creator=creator, 
        start_date=start_date,
        end_date=end_date,
        trades= trades,
        balances= balances,
        metrics = metrics
        )
    portfolio.save()
    return portfolio

def get_portfolio(creator, start_date, end_date):

    portfolio = portfolios.Portfolio.objects(
        creator = creator,
        start_date = start_date,
        end_date = end_date
    ).first()

    return portfolio

def get_all_versions(portfolio):

    creator_name = portfolio.creator.split('-')[0]
    
    versions = portfolios.Portfolio.objects(creator__contains=creator_name)

    return versions

def calculate_returns(balances):
    returns = dict()
    prev_bal = 1
    for date in balances:
        returns[date] = balances[date] / prev_bal
        prev_bal = balances[date]

    return returns

def calculate_metrics(balances):

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
            if previous_year     is not None:
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
        
    return metrics

def get_sp(start_date, end_date):
    portfolio = {}
    current_date = start_date
    while current_date <= end_date:
        portfolio[current_date] = ['spy']
        current_date = time.get_months_ahead(current_date, 1)

    return portfolio
    
def get_simulations(config):
    name = f'Simulation-{config["trade_period"]}x{config["trade_load"]}x{config["holding_period"]}'
    return portfolios.Portfolio.objects(creator=name)

def simulation_statistics(portfolio, simulations):

    # initalize simulation dict
    simulated_metrics = dict()
    probablities = dict()
    for metric in portfolio.metrics:
        simulated_metrics[metric] = []
        probablities[metric] = 0


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