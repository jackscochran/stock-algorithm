# Stock Predictor Model Learning Enviroment

Enviroment to define, train, and test algorithms and to create stock portfolios with 25 year backtests.

## feature_dev:

This script extracts financial data for various companies from the API provided by FMP, calculates relevant features and targets, and saves them to the database as training data points. The goal is to use this data to train a machine learning model that can predict the relative return of a stock over a certain period of time.

## algorithm_dev

This script is responsible for defining and training machine learning models for stock prediction. The script loads training data from the database, cleans and normalizes the training data, and then trains a model using that data. The script currently supports several different prediction algorithms and feature extraction techniques, which can be selected by modifying the algorithm and extractor variables at the beginning of the script.

## algorithm_test

This script is used to test the performance of an evaluation algorithm by running a series of tests on it to assess its accuracy.

The first test performed is the correlation test, which compares the performance of the algorithm for the top and bottom percentile of stock returns. The script then performs residual analysis, which compares the predicted values from the algorithm with the actual values. This includes calculating the root mean square error, mean absolute error, and mean absolute percentage error. The script also plots the residuals over time, as well as the predicted and actual values.

The script also calculates the return on investment (ROI) of the algorithm, and plots the cumulative returns over time. Finally, the script compares the performance of the algorithm to a benchmark, such as the S&P 500 index.


## portfolio_dev

This script is used to take the predictions created by an algorithm and use them to create a portfolio over a given time range. 

The main function in this script is to calculate the trades made over a given period of time. The aglorithm works by iterating from the start to end date by the trade period, and for each period taking the top n rated stocks at that time, where n is the trade_load. It stores these trades into a dictionary with dates as keys, and saves it to the database


## portfolio_test

This script is responsible for testing the performance of a portfolio built from a given model's predictions. The script does this by comparing the portfolio's performance to that of the S&P 500 index and through simulations of potential returns.

Performance metrics used include:
 - annual sharpe 
 - average annual returns 
 - annual stdev
 - annual downside
 - periodic sharpe 
 - average periodic returns 
 - periodic stdev
 - periodic downside