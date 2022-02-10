
from database import manager
from database.helpers import plots
from database.adaptors import portfolios as portfolio_adaptor
import statistics

import pprint

# ---------------------- RUNNER PROGRAM ---------------------- #

if __name__ == '__main__':

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


    # get portfolio and sp500 data #
    manager.setup_connection()
    portfolio = portfolio_adaptor.get_portfolio(config)
    sp_bal = portfolio_adaptor.sp500_balances(config['start_date'], config['end_date'], config['trade_period'])
    sp_metrics = portfolio_adaptor.calculate_metrics(sp_bal, sp_bal)


    # Compare to simulations
    # sim_stats = portfolio_adaptor.simulation_statistics(portfolio, 97)
    # pprint.pprint(sim_stats)

    # get simulation return data 
    simulation_returns = portfolio_adaptor.get_simulation_returns(config)
    mean_returns = {}
    median_returns = {}
    for date in simulation_returns:
        mean_returns[date] = statistics.mean(simulation_returns[date])
        median_returns[date] = statistics.median(simulation_returns[date])

    # compare returns
    plots.plot_returns(sp_bal, portfolio, mean_returns, median_returns)

    # compare metrics #
    plotted_metrics = [
        'annual_sharpe', 
        'average_annual_returns', 
        'annual_stdev',
        'annual_downside',
        'periodic_sharpe', 
        'average_periodic_returns', 
        'periodic_stdev',
        'periodic_downside'
        ]

    plots.plot_metrics(sp_metrics, portfolio, plotted_metrics)
    # ************************ #


    # compare Versions and sp500 and plot selected variable in bar graph

    variables = ['algorithm']
    static_variables = list(set(list(config.keys())) - set(variables))
    metrics = ['annual_sharpe', 'median_annual_return', 'average_annual_returns', 'annual_downside', 'CAGR']

    versions = portfolio_adaptor.get_versions(config, static_variables)

    plots.plot_version_returns(versions, variables, sp_bal)
    plots.plot_version_metrics(versions, metrics, sp_metrics)

