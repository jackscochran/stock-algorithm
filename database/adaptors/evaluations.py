from ..data import evaluations
from ..data import companies
from ..adaptors import prices as price_adaptor
from ..adaptors import evaluators as evaluator_adaptor 
from ..helpers import time
import math

def test_evaluations(evaluator_name, type):

    evaluator = evaluator_adaptor.get_evaluator(evaluator_name)
    testing_set = evaluations.Prediction.objects(evaluator_name=evaluator_name)

    if type == 'prediction':
        r_square = 0
        num = 0
        for evaluation in testing_set:
            predicted_value = evaluation.value
            actual_value = price_adaptor.get_performance(evaluation.ticker, evaluation.date, evaluator.holding_period)

            if actual_value is not None:
                r_square += math.pow((predicted_value-actual_value), 2)
                num += 1

        return r_square / num

    if type == 'rating':
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

def create_portfolio(date, size, evaluator_key):
    
    evaluator = evaluator_adaptor.get_evaluator(evaluator_key)
    predictions = evaluations.Evaluation.objects(
        date=date,
        type=evaluator.config['output_type'],
        evaluator_name = evaluator_key
    ).order_by('-value')

    portfolio = []
    for prediction in predictions:
        if len(portfolio) == size:
            return portfolio

        portfolio.append(prediction.ticker)

    return portfolio # case when portfolio size > number of evaluations