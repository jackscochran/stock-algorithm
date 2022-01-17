from ..helpers import visualization as viz
from ..adaptors import portfolios as portfolio_adaptor
import pandas as pd

def plot_returns(sp_bal, portfolio):
    viz.plot_against({
        'sp500': pd.Series(sp_bal),
        'portfolio': pd.Series(portfolio.balances)
    })
    viz.plot_against({
        'sp500': pd.Series(portfolio_adaptor.calculate_returns(sp_bal)),
        'portfolio': pd.Series(portfolio_adaptor.calculate_returns(portfolio.balances))
    })

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
    plot_data = dict()
    if versions is not None:
        for version in versions:
            plot_data[version] = pd.Series(versions[version].balances)

    if sp_bal:
        plot_data['S&P500'] = pd.Series(sp_bal)

    viz.plot_against(plot_data, legend_title=f'{str(variables)}')
    
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