from database.data.prices import MonthlyPrice
from ..data import evaluations
from ..data import companies
from ..adaptors import prices as price_adaptor
from ..adaptors import evaluators as evaluator_adaptor 
from ..helpers import time
from ..helpers import visualization as viz
import math
import heapq

import pandas as pd

def test_evaluations(evaluator):

    evaluator = evaluator_adaptor.get_evaluator(evaluator.key)
    testing_set = evaluations.Evaluation.objects(evaluator_name=evaluator.key)
    
    if evaluator.config['output_type'] == 'price_prediction':
        # get r^2 of percentage off
        residuals = []
        size = 100
        for evaluation in testing_set:

            if len(residuals) == size:
                break

            price = price_adaptor.get_monthly_price(evaluation.ticker, evaluation.date)
            actual_value = price_adaptor.get_performance(evaluation.ticker, evaluation.date, evaluator.config['holding_period'])
            if price is None or actual_value is None:
                continue
            predicted_value = evaluation.value/price.value

            if actual_value is not None:
                residuals.append(predicted_value - actual_value)

        viz.plot_hist(residuals, 50, max=1000, title='Residuals')

    if evaluator.config['output_type'] == 'rating':
        # testing metrics for rating evalutation
        # - average performance comparision of top and bottom 10 percentile of ratings
        # - correlation between rating and the actual performance
        return 

def add_evaluation(ticker, type, evaluator_name, date, value):
    evaluation = evaluations.Evaluation(
        ticker=ticker,
        type=type,
        evaluator_name=evaluator_name,
        date=date,
        value=value
    )

    evaluation.save()

def get_evaluations(tickers, evaluator_key, start_date, end_date):

    evals = evaluations.Evaluation.objects(
        ticker__in=tickers,
        evaluator_name=evaluator_key,
        date__gte=start_date,
        date__lte=end_date
    )

    return evals

def create_portfolio(date, size, evaluator_key, lookback):

    def heapsort(iterable):
        h = []
        for value in iterable:
            heapq.heappush(h, value)
        return[heapq.heappop(h) for i in range(len(h))]

    # get evaluattions
    evaluator = evaluator_adaptor.get_evaluator(evaluator_key)
    predictions = evaluations.Evaluation.objects(
        date__lte=date,
        date__gte=time.get_months_ahead(date, -lookback),
        type=evaluator.config['output_type'],
        evaluator_name = evaluator_key,
    ).order_by('-value')

    # get performance predictions
    portfolio = []
    performances = []

    if evaluator.config['output_type'] == 'relative_return':
        for prediction in predictions:
            portfolio.append(prediction.ticker)

            if len(portfolio) == size:
                return portfolio

    if evaluator.config['output_type'] == 'price_prediction':
        for prediction in predictions:
            current_price = price_adaptor.get_monthly_price(prediction.ticker, prediction.date)
            if current_price is None:
                continue

            performance = (prediction.value / current_price.value)
            performances.append((performance, prediction.ticker))

        performances = heapsort(performances)

        # create portfolio
        for i in range(size):
            portfolio.append(performances[len(performances)-i-1][1])

        return portfolio

def plot_predictions(evaluator, tickers):

    for ticker in tickers:
        price_range = price_adaptor.price_monthly_range(
        ticker, 
        evaluator.config['train_start'], 
        evaluator.config['train_end']
        )

        range = dict()
        for price in price_range:
            range[price.date] = price.value

        predictions = dict()
        actual=dict()
        for eval in get_evaluations([ticker], evaluator.key, evaluator.config['train_start'], evaluator.config['train_end']):
            current_date = time.get_months_ahead(eval.date, evaluator.config['holding_period'])
            predictions[current_date] = eval.value * range[eval.date]
            actual[current_date] = range[current_date]

        viz.plot_against({
            'predictions': pd.Series(predictions), 
            'actual': pd.Series(actual)
        }, title=f'{ticker}-Prices')

