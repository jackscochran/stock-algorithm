import pandas as pd
from ...adaptors import training_data as training_data_adaptor
from ...adaptors import companies as company_adaptor
from ... import manager
import math
import statistics

# load features

def load_features():

    ID = 2
    manager.setup_connection()

    # loop through training set 1, collecting sector averages
    standards = {}
    from_set = 1
    prev_evaluator = training_data_adaptor.get_training_set(from_set)

    for point in training_data_adaptor.get_training_points(from_set):
        print(point.date)
        features = {}
        for i in range(len(prev_evaluator.feature_labels)):
            features[prev_evaluator.feature_labels[i]] = point.feature_values[i]

        company = company_adaptor.get_company(point.ticker)
        if company is None:
            continue
        if company.sector not in list(standards.keys()):
            # initalize
            standards[company.sector] = {}
            for feature in list(features.keys()):
                standards[company.sector][feature] = []

        is_clean = True
        for feature in features:
            # add to list of relatable companies

            # check if clean
            if math.isnan(features[feature]) or features[feature] == 0:
                is_clean = False
                features[feature] = 0
            else:
                standards[company.sector][feature].append(features[feature])
                features[feature] -= statistics.median(standards[company.sector][feature])

        # add training set if it does not exist
        training_set = training_data_adaptor.get_training_set(ID)
        if training_set is None:
            training_data_adaptor.add_training_set(ID, list(features.keys()))

        # add feature set
        training_data_adaptor.add_training_point(ID, point.ticker, point.date, list(features.values()), is_clean)
        
        
