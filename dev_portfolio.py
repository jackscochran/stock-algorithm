import json

from portfolios import trades
from helpers import visualization as viz
from database import manager
from database.adaptors import portfolios as portfolio_adaptor
from database.adaptors import evaluators as evaluator_adaptor

import pandas as pd
import pprint


# ---------------------- MAIN FUNCTIONS ---------------------- #

def generate_portfolio_trades(trading_plan, config):
    portfolio_size = config['trade_load'] * config['holding_period'] / config['trade_period']
    balances = trades.trade_returns(
        trading_plan, 
        config['trade_period'], 
        portfolio_size,
        csv_name=f'{config["algorithm"]}-{config["version"]}')
    
    portfolio = portfolio_adaptor.add_portfolio(
        evaluator_adaptor.get_key(config),
        config['start_date'],
        config['end_date'],
        trading_plan,
        balances) 
    
    return portfolio

def visualize(portfolio, simulations):

    
    # balances plot
    sp = portfolio_adaptor.get_portfolio('sp-index', portfolio.start_date, portfolio.end_date)
    viz.plot_against({
        portfolio.creator: pd.Series(portfolio.balances),
        's&p': pd.Series(sp.balances)
    })

    # returns plot
    sp_returns = portfolio_adaptor.calculate_returns(sp.balances)
    port_returns = portfolio_adaptor.calculate_returns(portfolio.balances)
    viz.plot_against({
        portfolio.creator: pd.Series(port_returns),
        's&p': pd.Series(sp_returns)
    })

    # time series comparing portfolio versions
    versions = portfolio_adaptor.get_all_versions(portfolio)
    balances = dict()
    max_sharpe = 3
    max_version = 0

    for version in versions:
        balances[version.creator] = pd.Series(version.balances)

        if version.metrics['annual_sharpe'] < max_sharpe:
            max_sharpe = version.metrics['annual_sharpe']
            max_version = version.creator

    print(max_version)
    viz.plot_against(balances)


    # TODO
    return 

# ---------------------- RUNNER PROGRAM ---------------------- #

if __name__ == '__main__':

    # load algorithm configurations #
    config_file = open('algo_config.json')
    config = json.load(config_file)
    config_file.close()

    manager.setup_connection()

    # generate, test and visualize portfolio # 
    # trading_plan = trades.get_trades(config)
    # portfolio = portfolio_adaptor.get_portfolio('connorPOC-1', config['start_date'], config['end_date'])
    n = 200
    data = pd.read_csv('portfolios.csv')
    for i in range(1,25):   
        config['version'] = i
        config['trade_load'] = i
        trading_plan = portfolio_adaptor.load_portfolio(data, config)
        portfolio = generate_portfolio_trades(trading_plan, config)
        simulations = trades.simulate(n, config)

    # pprint.pprint(portfolio_adaptor.simulation_statistics(portfolio, simulations))
    # visualize(portfolio, simulations)