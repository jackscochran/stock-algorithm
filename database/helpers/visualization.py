import pandas as pd
from matplotlib import pyplot as plt
from pandas import plotting as pd_plt

def scatter_plot(x,y, model=None, title=None):
    plt.scatter(x,y)

    if model:
        plt.plot(x, model)

    if title:
        plt.title(title)

    plt.show()

def plot_time_series(series, title=None):
    plt.axhline(y=0, c="grey", label="y=0")
    series.plot()
    if title:
        plt.title(title)
        plt.axhline(y=0, c="black", label="y=0")
    plt.show()

def plot_against(series_dict, legend_title=None, title=None):
    plt.axhline(y=0, c="grey", label="y=0")
    for key in series_dict:
        plt.plot(series_dict[key], label=key)
    if legend_title:
        plt.legend(title=legend_title)
    if title:
        plt.title(title)

    # plt.gca().set_ylim([0.5, 2])
    plt.show()

def hist(series, title=None):
    series.hist(bins=30)
    if title:
        plt.title(title)
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