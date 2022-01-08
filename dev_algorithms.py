import json

from database import manager
from database.adaptors import evaluators as evaluator_adaptor
from database.adaptors import evaluations as evaluation_adaptor
from database.adaptors import prices as price_adaptor
from database.adaptors import training_data as training_data_adaptor
from algorithms import linearRegression
from helpers import time

ALGORITHM = linearRegression

# -------------- load algorithm configurations -------------- #

config_file = open('algo_config.json')
config = json.load(config_file)
config_file.close()

# -------------- Save evaluator information to database if not there ------------

manager.setup_connection()
evaluator = evaluator_adaptor.get_evaluator(evaluator_adaptor.get_key(config))
if evaluator is None:
    evaluator = evaluator_adaptor.add_evaluator(config)


# ---------------------- Iterate start-end, training and predicting stocks each month ---------------------- #

current_date = config['start_date']
while current_date < config['end_date']:

    print(f'Current Date: {current_date}')

    # ---------------------- Train Model ----------------------  #

    training_start = time.get_months_ahead(current_date, -36)
    training_stop = current_date

    X, y = training_data_adaptor.get_training_data(
        config['training_set_id'], 
        training_start, 
        training_stop
        )

    model = ALGORITHM.train(X, y)

    # ---------------------- Make Predictions ----------------------  #

    tickers, evaluation_data = training_data_adaptor.get_evaluation_data(
        config['training_set_id'],
        current_date,
        current_date
        )

    for i in range(len(tickers)):
        X = evaluation_data[i]
        evaluation = ALGORITHM.evaluate(model, X)
        
        current_price = price_adaptor.get_monthly_price(tickers[i], current_date)

        if current_price is not None:

            evaluation_adaptor.add_evaluation(
                tickers[i],
                config['output_type'],
                evaluator.key,
                current_date,
                evaluation/current_price.value
            )

    current_date = time.get_months_ahead(current_date, 1)


# ---------------------- TEST PREDICTIONS ---------------------- #

# metrics = ALGORITHM.test_evaluations(config['evaluator_name'])

# ---------------------- VISUALIZE RESULTS --------------------- # 


