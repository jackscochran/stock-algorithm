import pandas as pd
from ...helpers import time
from ...helpers import mathematics as math_helper
from ...adaptors import training_data as training_data_adaptor
from ...adaptors import prices as price_adaptor
from ... import manager
import math

# load features based on changes over periods


def load_features():
    count = 0
    ID = 2
    prediction_period = 12
    target_type = 'relative_return'

    manager.setup_connection()

    for row in training_data_adaptor.get_training_points(1):
        count += 1
        print(count)

        previous = training_data_adaptor.get_training_point(1, row.ticker, time.get_months_ahead(row.date, -prediction_period))

        if previous is None:
            continue

        features = []

        for i in range(len(row.feature_values)):
            features.append(row.feature_values[i] - previous.feature_values[i])

        features.append(previous.target)

        

        # add training set if it does not exist
        previous_set = training_data_adaptor.get_training_set(1)

        training_set = training_data_adaptor.get_training_set(ID)
        if training_set is None:
            training_data_adaptor.add_training_set(
                ID, 
                previous_set.feature_labels + ['relative_return'],
                prediction_period, 
                target_type)

        # add feature set
        training_data_adaptor.add_training_point(
            ID, 
            row.ticker, 
            row.date, 
            features, 
            row.target,
            row.is_clean and previous.is_clean
            )

        
        
