import pandas as pd
from ...helpers import time
from ...helpers import mathematics as math_helper
from ...adaptors import training_data as training_data_adaptor
from ...adaptors import prices as price_adaptor
from ... import manager
import math

# load features

def load_features(data):

    ID = 1
    prediction_period = 12
    target_type = 'relative_return'

    manager.setup_connection()
    count = 0

    for row in data.iterrows():
        count += 1
        print(count)
        row = row[1]

        features = {
            'pb': math_helper.divide(row['year_end_stock_price'], row['Book Value Per Share * USD'] * row['Shares Mil']),
            'pe': math_helper.divide(row['year_end_stock_price'], row['Earnings Per Share USD']),
            'total_assets': row['Total Liabilities'] + row["Total Stockholders' Equity"],
            'current_assets': row['Total Current Assets'],
            'liabilities': row['Total Liabilities'],
            'current_liabilies': row['Total Current Liabilities'],
            'bookValue': row['Book Value Per Share * USD'] * row['Shares Mil'],
            'revenue': row['Revenue USD Mil'],
            'earnings': row['Net Income USD Mil'],
            'cash_from_op': row['Operating Cash Flow USD Mil'],
            'cash': row['Cash & Short-Term Investments'],
            'cap_ex': row['Cap Ex as a % of Sales'] * row['Revenue USD Mil'],
        }

        target = price_adaptor.get_performance(row['ticker'], row['periodEndDate'][:7], prediction_period)
        baseline = price_adaptor.get_performance('spy', row['periodEndDate'][:7], prediction_period)
        if target is None or baseline is None:
            is_clean = False
            target = -1
        else:
            is_clean = True
            target = target - baseline

            for feature in features:
                if math.isnan(features[feature]) or features[feature] is None:
                    is_clean = False
                    features[feature] = 0

        # add training set if it does not exist
        training_set = training_data_adaptor.get_training_set(ID)
        if training_set is None:
            training_data_adaptor.add_training_set(ID, list(features.keys()),prediction_period, target_type)

        # add feature set
        training_data_adaptor.add_training_point(
            ID, 
            row['ticker'], 
            row['periodEndDate'][:7], 
            list(features.values()), 
            target,
            is_clean)

        
        
