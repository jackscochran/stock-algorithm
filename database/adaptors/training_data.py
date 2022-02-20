from ..data import training_data
from ..adaptors import companies as company_adaptor

import random
import math

import numpy as np

def get_training_point(identifier, ticker, date):
    return training_data.TrainingPoint.objects(training_set_id=identifier, ticker=ticker, date=date, is_clean=True).first()

def get_training_set(idenifier):
    return training_data.TrainingSet.objects(idenifier=idenifier).first()

def get_training_points(idenifier):
    return training_data.TrainingPoint.objects(training_set_id=idenifier).order_by('date')

def get_prediction_period(idenifier):
    training_set = get_training_set(idenifier)

    if training_set is None:
        return training_set

    return training_set.prediction_period

def add_training_set(identifier, features, target_type, config):
    training_set = training_data.TrainingSet(idenifier=identifier, feature_labels=features, config=config, target_type=target_type)
    training_set.save()
    return training_set

def add_training_point(id, ticker, date, features, target, is_clean):
    training_point = training_data.TrainingPoint.objects(training_set_id=id, ticker=ticker, date=date).first()

    if training_point is None:
        training_point = training_data.TrainingPoint(
            training_set_id=id,
            ticker=ticker,
            date=date,
            )

    training_point.feature_values = features
    training_point.target = target
    training_point.is_clean = is_clean

    training_point.save()

    return training_point
    
def get_training_data(id, start_date, end_date, string_filters, float_filters):
    

    training_rows = training_data.TrainingPoint.objects(
        training_set_id=id,
        date__lte=end_date, 
        date__gte=start_date,
        is_clean=True
        )
    
    tickers = []
    dates = []
    x = []
    y = []
 
    for row in training_rows:

        # Apply Filters
        profile = company_adaptor.get_company(row.ticker).profile
        is_match = True

        for filter in string_filters:
            if len(string_filters[filter]) == 0:
                continue
            is_match = is_match and (profile[filter] in string_filters[filter])
        for filter in float_filters:
            if len(float_filters[filter]) == 0:
                continue
            is_match = is_match and (profile[filter] in float_filters[filter])


        # save training data
        if is_match:
            tickers.append(row.ticker)
            dates.append(row.date)
            x.append(row.feature_values)
            y.append(row.target)
        
    x = np.array(x)
    y = np.array(y)
    
    return tickers, dates, x, y

def get_target_type(id):
    data_set = get_training_set(id)
    if data_set is None:
        return None

    return data_set.target_type

def delete_training_set(id):
    # get_training_set(id).delete()
    input('Are you sure you want to delete')
    for training_point in get_training_points(id):
        training_point.delete()