import pandas as pd
from matplotlib import pyplot as plt
from pandas import plotting as pd_plt

def plot_time_series(series):
    series.plot()
    plt.show()

def plot_against(series_dict, legend_title=None, title=None):
    for key in series_dict:
        plt.plot(series_dict[key], label=key)
    if legend_title:
        plt.legend(title=legend_title)
    if title:
        plt.title(title)
    plt.show()

def hist(series):
    series.hist()
    plt.show()

def scatter(x, y):
    plt.scatter(x, y)
    plt.show()

def lag_plot(series, lookback):
    pd_plt.lag_plot(series, lag=lookback)
    plt.show()

def plot_forecasts(train, predicted, actual):
    plot_against({
        predicted, actual
    })

def df_bar(df, legend_title=None, x=None, y=None):
    df.plot.bar(rot=0, x=x, y=y)
    if legend_title:
        plt.legend(title=legend_title)
    plt.show()

def plot_hist(series, bins, title=None, max=None):

    if max:
        for el in series:
            if el > max:
                series.remove(el)

    pd.Series(series).plot.hist(bins=bins)

    if title:
        plt.plot(title)

    plt.show()