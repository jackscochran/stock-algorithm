import json
from sklearn.ensemble import RandomForestRegressor

from sklearn.tree import plot_tree
from matplotlib import pyplot as plt

from database import manager
from database.adaptors import evaluators as evaluator_adaptor
from database.adaptors import evaluations as evaluation_adaptor
from database.adaptors import prices as price_adaptor
from database.adaptors import training_data as training_data_adaptor
from database.helpers import mathematics as math_helper
from algorithms.predictors import decisionTreeReg
from algorithms.predictors import linearRegression
from algorithms.predictors import randomForest
from algorithms.predictors import mlpRegressor
from algorithms.predictors import algoC
from algorithms.predictors import algoC_LinearReg
from algorithms.feature_extractors import randomForest as rf_extractor
from helpers import time

import numpy as np


# ----------------------    RUNNER  ---------------------- #

if __name__=="__main__":

    manager.setup_connection()


# -------------- load algorithm configurations -------------- #

    config = {
        "version": 9,
        "change_log": 'Consumer Defensive',
        "train_start": "1995-05",
        "train_end": "2021-08",
        "training_set_id": 2, 
        "training_timestep": 3,
        "training_lookback": 60,
        "string_filter": {
            "symbol": [],
            "currency": [],
            "industry": [],
            "exchangeShortName": [],
            "ceo": [],
            "sector": ['Consumer Defensive'],
            "country": ["US"],
        },
        "float_filter": {
            # [min, max]
            "price": [],  
            "beta": [], 
            "mktCap": [],
            "fullTimeEmployees": []
        }
    }

    algorithm = randomForest
    extractor = None

    training_set = training_data_adaptor.get_training_set(config['training_set_id'])
    config['holding_period'] = training_set.config['prediction_period']
    config['output_type'] = training_set.target_type
    config['name'] = algorithm.NAME
    config['random_grid'] = algorithm.RANDOM_GRID

    if extractor:
        config['extractor'] = extractor.NAME
    

# -------------- Save evaluator information to database if not there ------------

    evaluator = evaluator_adaptor.get_evaluator(evaluator_adaptor.get_key(config))
    if evaluator is None:
        evaluator = evaluator_adaptor.add_evaluator(config)

    # evaluation_adaptor.delete_evaluations(evaluator_adaptor.get_key(config))

# ---------------------- Iterate start-end, training and predicting stocks each month ---------------------- #


    print('----------- Getting Data')
    # evaluator.config['train_start'] = '2010-08'
    training_start = time.get_months_ahead(evaluator.config['train_start'], -evaluator.config['training_lookback'])
    training_stop = time.get_months_ahead(evaluator.config['train_start'], -evaluator.config['holding_period'])
    
    # Load Historical Data
    
    training_data = dict()
    current_date = training_start
    while current_date <= training_stop:
        print(current_date)
        training_tickers, dates, train_X, y = training_data_adaptor.get_training_data(
        evaluator.config['training_set_id'], 
        current_date + '-01', 
        current_date + '-31',
        config['string_filter'],
        config['float_filter']
        )

        if len(training_tickers) > 0:
            training_data[current_date] = {
                'tickers': training_tickers,
                'X': train_X,
                'y': y
        }
        current_date = time.get_months_ahead(current_date, config['training_timestep'])

    current_date = evaluator.config['train_start']
    while current_date <= evaluator.config['train_end']:

        print(f'\n----------- CURRENT DATE: {current_date} -----------')

        # ---------------------- Train Model ----------------------  

        # format and normalize data

        tickers = None
        X = None
        y = None
        for date in training_data:
            if tickers is None:
                tickers = training_data[date]['tickers']
                X = training_data[date]['X']
                y = training_data[date]['y']
            else:
                tickers += training_data[date]['tickers']
                X = np.concatenate((training_data[date]['X'], X))
                y = np.concatenate((training_data[date]['y'], y))

        train_means = [X[:,i].mean() for i in range(X.shape[1])]
        train_stds = [X[:,i].std() for i in range(X.shape[1])]
        X = np.array(math_helper.normalize_features(X, train_means, train_stds))

        # get data for next time step predictions

        tickers, dates, new_X, unrequired_y = training_data_adaptor.get_training_data(
            evaluator.config['training_set_id'],
            current_date + '-01', 
            current_date + '-31',
            config['string_filter'],
            config['float_filter']
            )
        evaluation_data = math_helper.normalize_features(new_X, train_means, train_stds)

        # extract important features

        if extractor:
            X, evaluation_data = extractor.extract(X, y, evaluation_data)


        print(f'----------- Training Model on {len(y)}')

        model = algorithm.train(X, y)

        algorithm.feature_analysis(model, training_set.feature_labels)

       
        # ---------------------- Make Predictions ----------------------  #

        print('----------- Making Predictions')
        for i in range(len(tickers)):
            evaluation_adaptor.add_evaluation(
                tickers[i],
                evaluator.config['output_type'],
                evaluator.key,
                current_date,#dates[i],
                algorithm.evaluate(model, evaluation_data[i])
            )

        # save to training_data for next period
        training_data.pop(time.get_months_ahead(current_date, -config['training_lookback']), None)
        training_data[current_date] = {
            'tickers': tickers,
            'X': new_X,
            'y': unrequired_y
        }

        current_date = time.get_months_ahead(current_date, config['training_timestep'])




