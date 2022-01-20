from database.loaders.feature_sets import one, delta
from database.adaptors import companies as company_adaptor
from database.adaptors import prices as price_adaptor
from database.adaptors import training_data as training_data_adaptor
from database.adaptors import fmp_cache as fmp_adaptor
from helpers import time
from database import manager


import json
import math

import pandas as pd

# -------------- load algorithm configurations -------------- #

# -------------- load features ------------------ #

SET_ID = 1
PREDICTION_TYPE = 'relative_return'
config = {
    'prediction_period': 3,
    'baseline': 'spy'
    }


manager.setup_connection()

tickers = company_adaptor.get_all_tickers()

count = 0
for ticker in tickers:

    # Log Process
    print('\n---------------------------\n')
    print(f'{ticker} - {count} / {len(tickers)}')
    count += 1
   
    # Get Historical Financial Data
    data_sources = {
        'income_statements': f'v3/income-statement-growth/{ticker.upper()}?period=quarter',
        'balance_sheets': f'v3/balance-sheet-statement-growth/{ticker.upper()}?period=quarter',
        'cashflow_statements': f'v3/cash-flow-statement-growth/{ticker.upper()}?period=quarter',
        'key_metrics': f'v3/key-metrics/{ticker.upper()}?period=quarter',
    }

    # Collect historcial data
    is_available = True
    for source in data_sources:
        data_sources[source] = fmp_adaptor.get_response(data_sources[source])
        if data_sources[source] is None:
            is_available = False
            break
    if not is_available:
        continue

    # Loop Through Periods and Save Data
    for i in range(0, len(data_sources['key_metrics'])-1):
        
        date = data_sources['income_statements'][i]['date'][:7]

        # Get Variables for Alpha
        previous_return = price_adaptor.get_performance(
            ticker,
            time.get_months_ahead(date, -config['prediction_period']),
            config['prediction_period']
        )
        future_return = price_adaptor.get_performance(
            ticker,
            date,
            config['prediction_period'],
        )
        previous_baseline = price_adaptor.get_performance(
            config['baseline'],
            time.get_months_ahead(date, -config['prediction_period']),
            config['prediction_period']
        )
        future_baseline = price_adaptor.get_performance(
            config['baseline'],
            date,
            config['prediction_period'],
        )
        if previous_return is None or previous_baseline is None:
            continue
        
        try:
            features = {
                'pe': data_sources['key_metrics'][i]['peRatio'] - data_sources['key_metrics'][i+1]['peRatio'],
                'assets': data_sources['balance_sheets'][i]['growthTotalAssets'],
                'current_assets': data_sources['balance_sheets'][i]['growthTotalCurrentAssets'],
                'liabilities': data_sources['balance_sheets'][i]['growthTotalLiabilities'],
                'current_liabilities': data_sources['balance_sheets'][i]['growthTotalCurrentLiabilities'],
                'book_value': data_sources['balance_sheets'][i]['growthTotalAssets'] - data_sources['balance_sheets'][i]['growthTotalLiabilities'],
                'revenue': data_sources['income_statements'][i]['growthRevenue'],
                'earnings': data_sources['income_statements'][i]['growthNetIncome'],
                'cash_from_op': data_sources['cashflow_statements'][i]['growthNetCashProvidedByOperatingActivites'],
                'cash_from_inv': -data_sources['cashflow_statements'][i]['growthNetCashUsedForInvestingActivites'],
                'cash_from_fin': data_sources['cashflow_statements'][i]['growthNetCashUsedProvidedByFinancingActivities'],
                'cash': data_sources['balance_sheets'][i]['growthCashAndCashEquivalents'],
                'capex_per_share': data_sources['key_metrics'][i]['capexPerShare'] - data_sources['key_metrics'][i+1]['capexPerShare'],
                'pb': data_sources['key_metrics'][i]['pbRatio'] - data_sources['key_metrics'][i+1]['pbRatio'],
                'cash_per_share': data_sources['key_metrics'][i]['cashPerShare'] - data_sources['key_metrics'][i+1]['cashPerShare'],
                'current_ratio': data_sources['key_metrics'][i]['currentRatio'] - data_sources['key_metrics'][i+1]['currentRatio'],
                'net_margin': data_sources['income_statements'][i]['growthGrossProfitRatio'],
                'roa': data_sources['key_metrics'][i]['returnOnTangibleAssets'] - data_sources['key_metrics'][i+1]['returnOnTangibleAssets'],
                'eps': data_sources['income_statements'][i]['growthEPS'],
                'relative_return': previous_return - previous_baseline,
            }
        except TypeError:
            continue
        
        # Check if data is clean
        is_clean = future_return != None and future_baseline != None
        for feature in features:
            if math.isnan(features[feature]) or features[feature] is None:
                is_clean = False

        if is_clean:
            # add training set if it does not exist
            training_set = training_data_adaptor.get_training_set(SET_ID)
            if training_set is None:
                training_data_adaptor.add_training_set(
                    SET_ID, 
                    list(features.keys()),
                    PREDICTION_TYPE,
                    config
                    )

            # add feature set
            training_data_adaptor.add_training_point(
                SET_ID, 
                ticker, 
                date, 
                list(features.values()), 
                future_return - future_baseline,
                is_clean
                )



# -------------- Visualize feature data -------------- # 
