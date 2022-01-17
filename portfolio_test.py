
from database import manager
from database.helpers import plots
from database.adaptors import portfolios as portfolio_adaptor

# ---------------------- RUNNER PROGRAM ---------------------- #

if __name__ == '__main__':

    # load algorithm configurations #
    config = {
        "algorithm": "RandomForestRegressor-1",
        "start_date": "2014-01",
        "end_date": "2020-07",
        "holding_period": 12,
        "trade_load": 9,
        "trade_period": 1,  
        "lookback": 1
    }


    # get portfolio and sp500 data # 
    manager.setup_connection()
    portfolio = portfolio_adaptor.get_portfolio(config)
    sp_bal = portfolio_adaptor.sp500_balances(config['start_date'], config['end_date'], config['trade_period'])
    sp_metrics = portfolio_adaptor.calculate_metrics(sp_bal, sp_bal)


    
    # compare returns
    plots.plot_returns(sp_bal, portfolio)

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

    # plot alpha #
    plots.plot_excess(portfolio_adaptor.calculate_returns(portfolio.balances), portfolio_adaptor.calculate_returns(sp_bal))


    # compare Versions and sp500 and plot selected variable in bar graph

    static_variables = ['algorithm', 'holding_period', 'trade_period', 'lookback', 'start_date', 'end_date']
    variables = list(set(list(config.keys())) - set(static_variables))
    metrics = ['annual_sharpe', 'periodic_sharpe', 'mean_periodic_alpha']

    versions = portfolio_adaptor.get_versions(config, static_variables)

    plots.plot_version_returns(versions, variables, sp_bal)
    plots.plot_version_metrics(versions, metrics, sp_metrics)