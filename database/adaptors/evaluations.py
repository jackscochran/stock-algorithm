from database.data.prices import MonthlyPrice
from ..data import evaluations
from ..data import companies
from ..adaptors import prices as price_adaptor
from ..adaptors import evaluators as evaluator_adaptor 
from ..adaptors import training_data as training_data_adaptor 
from ..helpers import time
from ..helpers import visualization as viz

import random

import math
from scipy.stats import stats as scipy_stats 
import statistics
import heapq

import pandas as pd

def test_evaluations(evaluator):
    
    if evaluator.config['output_type'] == 'relative_return':
        evals = list(get_top_evaluations(evaluator.key))

        # correlation testing
        percentile = 0.01
        num_of_evals = len(evals)
        top = []
        bottom = []
        universe = []
        for i in range(int(percentile * num_of_evals)):
            high = training_data_adaptor.get_training_point(
                evaluator.config['training_set_id'],
                evals[i].ticker,
                evals[i].date
            )
            low = training_data_adaptor.get_training_point(
                evaluator.config['training_set_id'],
                evals[num_of_evals - i - 1].ticker,
                evals[num_of_evals - i - 1].date
            )
            if high is not None:
                top.append(high.target)
            if low is not None:
                bottom.append(low.target)

        # residual Anlysis
        residuals = []
        se = []
        ae = []
        ape = []
        se_over_time = dict()
        predictions = []
        actual = []

        count = 0
        outlier_count = 0
        outlier_definition = 100
        evals = get_all_evaluations(evaluator.key)
        for eval in evals:

            count += 1
            print(f'{count} / {len(evals)}')

            training_node = training_data_adaptor.get_training_point(
                evaluator.config['training_set_id'],
                eval.ticker,
                eval.date
            )

            if training_node is not None:
                residual = eval.value-training_node.target
                universe.append(training_node.target)
                if residual*residual > outlier_definition: # remove any outliers to fit on graph
                    outlier_count += 1
                    continue

                residuals.append(residual)
                se.append(residual * residual)
                ae.append(max(residual, -residual))
                ape.append(max(residual/training_node.target, -residual/training_node.target))
                predictions.append(eval.value)
                actual.append(training_node.target)

                if eval.date not in se_over_time.keys():
                    se_over_time[eval.date] = []

                se_over_time[eval.date].append(residual*residual)

        print(f'\nTop {percentile * 100}% mean: {statistics.mean(top)}')
        print(f'Bottom {percentile * 100}% mean: {statistics.mean(bottom)}')
        print(f'Universe mean: {statistics.mean(universe)}\n')

        print(f'Top {percentile * 100}% median: {statistics.median(top)}')
        print(f'Bottom {percentile * 100}% median: {statistics.median(bottom)}')
        print(f'Universe median: {statistics.median(universe)}\n')

        print(f'Root Mean Square Error: {math.sqrt(statistics.mean(se))}')
        print(f'Root Median Square Error: {math.sqrt(statistics.median(se))}')
        print('----------------------------------------------')
        print(f'Average Absolute Percent Error: {statistics.mean(ape)}')
        print(f'Median Absolute Percent Error: {statistics.median(ape)}')
        print('----------------------------------------------')
        print(f'Average Absoulte Error: {statistics.mean(ae)}')
        print(f'Median Absoulte Error: {statistics.median(ae)}\n')

        slope, intercept, r, p, std_err = scipy_stats.linregress(predictions, actual)
        print(f'Actual = ({slope}) * Prediction + ({intercept})')
        print(f'R: {r}')
        print(f'R^2: {r*r}')
        print(f'p-value: {p}')
        print(f'Std_err: {std_err}\n')

        def myfunc(x):
            return slope * x + intercept

        mymodel = list(map(myfunc, predictions))

        # plots 
        rMeanSE = {}
        rMedSE = {}
        for date in se_over_time:
            rMeanSE[date] = math.sqrt(statistics.mean(se_over_time[date]))
            rMedSE[date] = math.sqrt(statistics.median(se_over_time[date]))

        viz.plot_against({
            'Root Mean Square Error': pd.Series(rMeanSE),
            'Root Median Square Error': pd.Series(rMedSE)
        }, title="Square Error Over Time", legend_title='Error Type')

        viz.scatter_plot(predictions, actual, model=mymodel, title='Predictions vs Actual Alpha')


    if evaluator.config['output_type'] == 'rating':
        # testing metrics for rating evalutation


        # - average performance comparision of top and bottom 10 percentile of ratings
        # - correlation between rating and the actual performance
        return 

    if evaluator.config['output_type'] == 'classification':
        # testing metrics for classifier evalutation
        # - 
        # - 
        return 

def add_evaluation(ticker, type, evaluator_name, date, value):
    evaluation = evaluations.Evaluation.objects(ticker=ticker, date=date, evaluator_name=evaluator_name).first()

    if evaluation is None:
        evaluation = evaluations.Evaluation(
            ticker=ticker,
            type=type,
            evaluator_name=evaluator_name,
            date=date,
            value=value
        )
    evaluation.value = value
    evaluation.save()

def delete_evaluations(evaluator_key):
    for evaluation in get_all_evaluations(evaluator_key):
        evaluation.delete()

def get_evaluation(evaluator_key, ticker, date):
    return evaluations.Evaluation.objects(
        evaluator_name = evaluator_key,
        ticker = ticker,
        date = date
    ).first()


def get_evaluations(tickers, evaluator_key, start_date, end_date):

    evals = evaluations.Evaluation.objects(
        ticker__in=tickers,
        evaluator_name=evaluator_key,
        date__gte=start_date,
        date__lte=end_date
    )

    return evals

def get_evaluations(evaluator_key, start_date, end_date):

    evals = evaluations.Evaluation.objects(
        evaluator_name=evaluator_key,
        date__gte=start_date,
        date__lte=end_date
    )

    return evals

def get_all_evaluations(evaluator_key):
    return evaluations.Evaluation.objects(evaluator_name=evaluator_key).order_by('date')

def get_top_evaluations(evaluator_key):
    return evaluations.Evaluation.objects(evaluator_name=evaluator_key).order_by('-value')

def get_top_evaluations_by_date(evaluator_key, date):
    return evaluations.Evaluation.objects(evaluator_name=evaluator_key, date=date).order_by('-value')


def create_portfolio(date, size, evaluator_key, lookback, short):
    evaluator_keys =  [evaluator_key] # [f'RandomForestRegressor-{i}' for i in range(7, 18)] 
    # get evaluattions
    sort = '-value'
    if short:
        sort ='value'

    predictions = evaluations.Evaluation.objects(
        date__lte=date,
        date__gte=time.get_months_ahead(date, -lookback),
        evaluator_name__in = evaluator_keys,
    ).order_by(sort)

    # get performance predictions
    portfolio = []

    if evaluator_adaptor.get_evaluator(evaluator_key).config['output_type'] == 'relative_return' or evaluator_adaptor.get_evaluator(evaluator_key).config['output_type'] == 'stock_sharpe': # True
        for prediction in predictions:
            portfolio.append(prediction.ticker)

            if len(portfolio) == size:
                return portfolio

def sample_predictions(evaluator, tickers):

    for ticker in tickers:

        predictions = dict()
        actual=dict()
        residuals = []
        for eval in get_evaluations([ticker], evaluator.key, evaluator.config['train_start'], evaluator.config['train_end']):
            training_node = training_data_adaptor.get_training_point(
                evaluator.config['training_set_id'],
                ticker,
                eval.date
            )

            if training_node is not None:
                predictions[eval.date] = eval.value
                actual[eval.date] = training_node.target
                residuals.append(eval.value-training_node.target)

        print(f'Correlation with {ticker}: {scipy_stats.pearsonr(list(actual.values()),list(predictions.values()))}')

        viz.plot_against({
            'predictions': pd.Series(predictions), 
            'actual': pd.Series(actual)
        }, title=f'{ticker}-Prices', legend_title='Holdings')

        viz.hist(pd.Series(residuals), title='Residual Plot')

