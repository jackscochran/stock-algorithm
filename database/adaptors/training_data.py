from ..data import training_data
from ..adaptors import prices as price_adaptor
import numpy as np

def get_training_set(idenifier):
    return training_data.TrainingSet.objects(idenifier=idenifier).first()

def get_entire_set(idenifier):
    return training_data.TrainingPoint.objects(training_set_id=idenifier).order_by('date')

def add_training_set(identifier, features):
    training_set = training_data.TrainingSet(idenifier=identifier, feature_labels=features)
    training_set.save()

    return training_set

def get_feature_names(id):
    return training_data.TrainingSet().objects(id=id).first().feature_names

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
    
def get_training_data(id, start_date, end_date):
    

    training_rows = training_data.TrainingPoint.objects(
        training_set_id=id,
        date__lte=end_date, 
        date__gte=start_date, 
        is_clean=True
        )
    
    x = []
    y = []
 
    for row in training_rows:
        x.append(row.feature_values)
        y.append(row.target)
            
    x = np.array(x)
    y = np.array(y)
    
    return x, y

def get_evaluation_data(id, start_date, end_date):
    training_rows = training_data.TrainingPoint.objects(
        training_set_id=id,
        date__lte=end_date, 
        date__gte=start_date, 
        )
    
    x = []
    tickers = []
 
    for row in training_rows:
        tickers.append(
            row.ticker
        )

        x.append(
            row.feature_values
        )
            
    x = np.array(x)
    
    return tickers, x