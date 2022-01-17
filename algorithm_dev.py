import json

from database import manager
from database.adaptors import evaluators as evaluator_adaptor
from database.adaptors import evaluations as evaluation_adaptor
from database.adaptors import prices as price_adaptor
from database.adaptors import training_data as training_data_adaptor
from database.helpers import mathematics as math_helper
from algorithms import decisionTreeReg, linearRegression, randomForest
from helpers import time

import numpy as np


# ----------------------    RUNNER  ---------------------- #

if __name__=="__main__":

    manager.setup_connection()


# -------------- load algorithm configurations -------------- #

    config = {
        "version": 1,
        "train_start": "2014-01",
        "train_end": "2020-08",
        "training_set_id": 2, 
        "training_timestamp": 1,
        "training_lookback": 48
    }

    algorithm = randomForest

    config['holding_period'] = training_data_adaptor.get_prediction_period(config['training_set_id'])
    config['output_type'] = training_data_adaptor.get_target_type(config['training_set_id'])
    config['name'] = algorithm.NAME

# -------------- Save evaluator information to database if not there ------------

    evaluator = evaluator_adaptor.get_evaluator(evaluator_adaptor.get_key(config))
    if evaluator is None:
        evaluator = evaluator_adaptor.add_evaluator(config)

# ---------------------- Iterate start-end, training and predicting stocks each month ---------------------- #

    current_date = evaluator.config['train_start']
    while current_date < evaluator.config['train_end']:

        print(f'----------- CURRENT DATE: {current_date} -----------')

        # ---------------------- Train Model ----------------------  #

        print('----------- Getting Data')

        training_start = time.get_months_ahead(current_date, -config['training_lookback'])
        training_stop = time.get_months_ahead(current_date, -config['holding_period'])

        X, y = training_data_adaptor.get_training_data(
            evaluator.config['training_set_id'], 
            training_start, 
            training_stop
            )

        # normalize data
        train_means = [X[:,i].mean() for i in range(X.shape[1])]
        train_stds = [X[:,i].std() for i in range(X.shape[1])]
        X = np.array(math_helper.normalize_features(X, train_means, train_stds))

        print('----------- Training Model')

        model = algorithm.train(X, y)


        # ---------------------- Make Predictions ----------------------  #

        print('----------- Making Predictions')

        tickers, evaluation_data = training_data_adaptor.get_evaluation_data(
            evaluator.config['training_set_id'],
            current_date,
            current_date
            )

        # normalize data
        evaluation_data = np.array(math_helper.normalize_features(evaluation_data, train_means, train_stds))

        for i in range(len(tickers)):
            evaluation_adaptor.add_evaluation(
                tickers[i],
                evaluator.config['output_type'],
                evaluator.key,
                current_date,
                algorithm.evaluate(model, evaluation_data[i])
            )

        current_date = time.get_months_ahead(current_date, config['training_timestamp'])


# ---------------------- TEST PREDICTIONS ---------------------- #

# metrics = algorithm.test_evaluations(config['name'])

# ---------------------- VISUALIZE RESULTS --------------------- #     




