import pandas as pd
from matplotlib import pyplot as plt
from pandas import plotting as pd_plt

def plot(series):
    series.plot()
    plt.show()

def plot_against(series_dict):
    for key in series_dict:
        plt.plot(series_dict[key], label=key)
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
