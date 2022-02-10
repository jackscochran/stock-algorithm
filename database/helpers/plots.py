from ..helpers import visualization as viz
from ..adaptors import portfolios as portfolio_adaptor
import pandas as pd

def plot_returns(sp_bal, portfolio, mean_returns, median_returns):
    viz.plot_against({
        'SPY Index': pd.Series(sp_bal),
        'Portfolio': pd.Series(portfolio.balances)
    })
    viz.plot_against({
        'SPY Index': pd.Series(portfolio_adaptor.calculate_returns(sp_bal)),
        'Portfolio': pd.Series(portfolio_adaptor.calculate_returns(portfolio.balances)),
        'Mean Returns': pd.Series(mean_returns),
        'Median Returns': pd.Series(median_returns)
    }, legend_title='Comparisons',title=f'{portfolio.trade_period} Month Returns')

def plot_metrics(sp_metrics, portfolio, plotted_metrics):
   
    viz.df_bar(pd.DataFrame({
            'sp500': [sp_metrics[metric] for metric in plotted_metrics],
            'portfolio': [portfolio.metrics[metric] for metric in plotted_metrics]
        },
        index=plotted_metrics
    ))

def plot_excess(returns, baseline):
    alpha = portfolio_adaptor.calculate_alpha(returns, baseline)
    viz.plot_time_series(pd.Series(alpha))

def plot_version_returns(versions, variables, sp_bal=None):
    balances = dict()
    returns = dict()
    if versions is not None:
        for version in versions:
            balances[version] = pd.Series(versions[version].balances)
            returns[version] = pd.Series(portfolio_adaptor.calculate_returns(versions[version].balances))

    if sp_bal:
        balances['S&P500'] = pd.Series(sp_bal)
        returns['S&P500'] = pd.Series(portfolio_adaptor.calculate_returns(sp_bal))

    viz.plot_against(balances, legend_title=f'{str(variables)}')
    viz.plot_against(returns, legend_title=f'{str(variables)}')
    
def plot_version_metric(versions, metric, sp_metric=None):
    plot_data = {
        'versions': [],
        'value': []
    }

    if sp_metric:
        plot_data['versions'].append('SP500')
        plot_data['value'].append(sp_metric)

    if versions is not None:
        for version in versions:
            plot_data['versions'].append(version)
            plot_data['value'].append(versions[version].metrics[metric])

   
    viz.df_bar(pd.DataFrame(plot_data), x='versions', y='value')

def plot_version_metrics(versions, metrics, sp_metrics):
    plot_data = dict()

    for version in versions:
        plot_data[version] = [versions[version].metrics[metric] for metric in metrics]

    plot_data['SP500'] = [sp_metrics[metric] for metric in metrics]

    viz.df_bar(pd.DataFrame(plot_data, index=metrics))