from database.adaptors import companies as company_adaptor
from database.adaptors import prices as price_adaptor
from database.adaptors import evaluations as evaluation_adaptor
from database.adaptors import training_data as training_data_adaptor
from database.adaptors import fmp_cache as fmp_adaptor
from database.data.training_data import TrainingPoint
from helpers import time
from database.helpers import mathematics as math_helper
from database import manager

import math
import statistics

import pandas as pd

SET_ID = 1
PREDICTION_TYPE = 'relative_return'
config = {
    'prediction_period': 3,
    'baseline': 'spy'
    }

# -------------- helper functions -------------- #

def extract_from_api():
    tickers = company_adaptor.get_all_tickers()
    count = 0
    threshold = 0   
    for ticker in tickers:

        # Log Process
        print('\n---------------------------\n')
        print(f'{ticker} - {count} / {len(tickers)}')
        count += 1
        if count <= threshold:
            continue # to speed up process and avoid unessesary reentries
    
        # Get Historical Financial Data
        data_sources = {
            'income_statements': f'v3/income-statement-growth/{ticker.upper()}?period=quarter',
            'balance_sheets': f'v3/balance-sheet-statement-growth/{ticker.upper()}?period=quarter',
            'cashflow_statements': f'v3/cash-flow-statement-growth/{ticker.upper()}?period=quarter',
            # 'financial_ratios': f'v3/ratios/{ticker.upper()}?period=quarter',
            'key_metrics': f'v3/key-metrics/{ticker.upper()}?period=quarter'
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
            
            # all quarterly statements must be filed within 45 days at the end of the quarter
            try:
                date = time.get_days_ahead(data_sources['key_metrics'][i]['date'][:10], 45)
            except:
                continue
            # Get Variables for target
            current_target = price_adaptor.get_alpha(ticker, date, config['prediction_period'], config['baseline'])
            previous_target = price_adaptor.get_alpha(ticker, time.get_months_ahead(date, -config['prediction_period']), config['prediction_period'], config['baseline'])
            
            # current_target = price_adaptor.get_stock_sharpe_of_alpha(ticker, config['baseline'], date, config['prediction_period'], 7)
            # previous_target = price_adaptor.get_stock_sharpe_of_alpha(ticker, config['baseline'], time.get_months_ahead(date, -config['prediction_period']), config['prediction_period'], 7)

            try:
                features = {
                    'pe': math_helper.divide((data_sources['key_metrics'][i]['peRatio'] - data_sources['key_metrics'][i+1]['peRatio']), data_sources['key_metrics'][i+1]['peRatio']),
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
                    'capex_per_share': math_helper.divide((data_sources['key_metrics'][i]['capexPerShare'] - data_sources['key_metrics'][i+1]['capexPerShare']), data_sources['key_metrics'][i+1]['capexPerShare']),
                    'pb': math_helper.divide((data_sources['key_metrics'][i]['pbRatio'] - data_sources['key_metrics'][i+1]['pbRatio']), data_sources['key_metrics'][i+1]['pbRatio']),
                    'cash_per_share': math_helper.divide((data_sources['key_metrics'][i]['cashPerShare'] - data_sources['key_metrics'][i+1]['cashPerShare']), data_sources['key_metrics'][i+1]['cashPerShare']),
                    'current_ratio': math_helper.divide((data_sources['key_metrics'][i]['currentRatio'] - data_sources['key_metrics'][i+1]['currentRatio']), data_sources['key_metrics'][i+1]['currentRatio']),
                    'net_margin': data_sources['income_statements'][i]['growthGrossProfitRatio'],
                    'roa': math_helper.divide((data_sources['key_metrics'][i]['returnOnTangibleAssets'] - data_sources['key_metrics'][i+1]['returnOnTangibleAssets']), data_sources['key_metrics'][i+1]['returnOnTangibleAssets']),
                    'eps': data_sources['income_statements'][i]['growthEPS'],
                    'previous_target': previous_target
                }
            except (TypeError, IndexError) as e:
                continue
            
            # Check if data is clean (look for null values)
            is_clean = current_target != None
            for feature in features:
                if features[feature] is None or math.isnan(features[feature]):
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
                    current_target,
                    is_clean
                    )
    return

def extract_diff_from_category(from_set, category):

    current_date = None
    points_to_add = []
    source_set = training_data_adaptor.get_training_set(from_set)
    source_set_points = training_data_adaptor.get_training_points(from_set)
    start_date = None
    ignore = [19] # feature index to stay constant

     # add training set if it does not exist
    training_set = training_data_adaptor.get_training_set(SET_ID)
    if training_set is None:
        training_data_adaptor.add_training_set(SET_ID, source_set.feature_labels, PREDICTION_TYPE, config)

    for point in source_set_points:

        if start_date:
            if point.date < start_date:
                continue

        if current_date is None or current_date < point.date: 
            print(point.date)
            # new date, add new training points and reset standards
            for point_to_add in points_to_add:

                # get difference from category
                company = company_adaptor.get_company(point_to_add.ticker)
                is_clean = len(standards[company.profile[category]][0]) > 7 and point_to_add.is_clean# make sure to have at least 7 samples to take average from
                features = []
                for i in range(len(point_to_add.feature_values)):
                    if i not in ignore:
                        features.append(point_to_add.feature_values[i] - statistics.median(standards[company.profile[category]][i]))
                    else:
                        features.append(point_to_add.feature_values[i])

                training_data_adaptor.add_training_point(
                    id=SET_ID,
                    ticker = point_to_add.ticker,
                    date = point_to_add.date,
                    features=features,
                    target = point_to_add.target,
                    is_clean=is_clean
                )

            current_date = point.date
            standards = {} 
            points_to_add = []

        
        # get category and inilize if needed
        company = company_adaptor.get_company(point.ticker)
        if company is None:
            continue

        # register point to save later with category data
        points_to_add.append(point)

        if company.profile[category] not in list(standards.keys()):
            # initalize
            standards[company.profile[category]] = []
            for feature in source_set.feature_labels:
                standards[company.profile[category]].append([])

        # save point data to category
        for i in range(len(point.feature_values)):
            standards[company.profile[category]][i].append(point.feature_values[i])
        
    return

def extract_from_feature_set(from_set):
    # loop through training set 1, collecting sector averages
    standards = {}
    prev_evaluator = training_data_adaptor.get_training_set(from_set)

    for point in training_data_adaptor.get_training_points(from_set):
        print(point.date)
        features = {}
        for i in range(len(prev_evaluator.feature_labels)):
            features[prev_evaluator.feature_labels[i]] = point.feature_values[i]

        company = company_adaptor.get_company(point.ticker)
        if company is None:
            continue
        if company.profile["sector"] not in list(standards.keys()):
            # initalize
            standards[company.profile["sector"]] = {}
            for feature in list(features.keys()):
                standards[company.profile["sector"]][feature] = []

        is_clean = True
        for feature in features:
            # add to list of relatable companies

            # check if clean
            if math.isnan(features[feature]) or features[feature] == 0:
                is_clean = False
                features[feature] = 0
            else:
                standards[company.profile["sector"]][feature].append(features[feature])
                features[feature] -= statistics.median(standards[company.profile["sector"]][feature])

        # add training set if it does not exist
        training_set = training_data_adaptor.get_training_set(SET_ID)
        if training_set is None:
            training_data_adaptor.add_training_set(SET_ID, list(features.keys()), PREDICTION_TYPE, config)

        # add feature set
        training_data_adaptor.add_training_point(SET_ID, point.ticker, point.date, list(features.values()), point.target,is_clean)
        
    return

def extract_from_predictions(from_set, models):
     # add training set if it does not exist
    training_set = training_data_adaptor.get_training_set(SET_ID)
    if training_set is None:
        training_data_adaptor.add_training_set(SET_ID, models, PREDICTION_TYPE, config)


    for point in training_data_adaptor.get_training_points(from_set):
        print(point.date)
        features = []
        for model in models:
            prediction = evaluation_adaptor.get_evaluation(model, point.ticker, point.date)
            if prediction:
                features.append(prediction.value)

        if len(features) == len(models):
            training_data_adaptor.add_training_point(SET_ID, point.ticker, point.date, features, point.target, point.is_clean)

# -------------- load features ------------------ #


manager.setup_connection()


# training_data_adaptor.delete_training_set(SET_ID)
# extract_diff_from_category(2, 'sector')
# extract_from_predictions(2, ['RandomForestRegressor-2', 'AlgoCLinReg-2'])
extract_from_api()


