import pandas as pd
from ...helpers import time
from ...adaptors import training_data as training_data_adaptor
from ...adaptors import prices as price_adaptor
from ... import manager
import math

# load features

def load_features(data):

    ID = 1
    manager.setup_connection()

    for row in data.iterrows():
        row = row[1]

        features = {
            'bookValue': row['Book Value Per Share * USD'],
            'revenueGrowth': row['Revenue Growth'],
            'currentPrice': row['avgMonthlyPrice'],
            'eps': row['Earnings Per Share USD'],
            'epsSQ': row['Earnings Per Share USD'] * row['Earnings Per Share USD'],
            'operatingMargin': row['Operating Margin %'],
            'freeCashFlowPerShare': row['Free Cash Flow Per Share * USD'],
            'interestCoverage': row['Interest Coverage'],
            'interestCoverageSQ': row['Interest Coverage']*row['Interest Coverage'],            
            'quickRatio': row['Quick Ratio'],
            'quickRatioSQ': row['Quick Ratio']*row['Quick Ratio'],
            'debtToEquity': row['Debt/Equity'],
            'debtToEquitySQ': row['Debt/Equity']*row['Debt/Equity'],
            'assetTurnover': row['Asset Turnover'],
            'assetTurnoverSQ': row['Asset Turnover']*row['Asset Turnover']
        }

        target = price_adaptor.get_monthly_price(row['ticker'], time.get_months_ahead(row['periodEndDate'][:7], 12))
        if target is None:
            is_clean = False
            target = -1
        else:
            is_clean = True
            target = target.value

            for feature in features:
                if math.isnan(features[feature]) or features[feature] is None:
                    is_clean = False
                    features[feature] = 0

        # add training set if it does not exist
        training_set = training_data_adaptor.get_training_set(ID)
        if training_set is None:
            training_data_adaptor.add_training_set(ID, list(features.keys()))

        # add feature set
        training_data_adaptor.add_training_point(
            ID, row['ticker'], 
            row['periodEndDate'][:7], 
            list(features.values()), 
            target,
            is_clean)
        
        
