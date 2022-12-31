
from database import manager
from database.adaptors import evaluators as evaluator_adaptor
from database.adaptors import evaluations as evaluation_adaptor
from database.adaptors import prices as price_adaptor
from database.adaptors import training_data as training_data_adaptor
from helpers import time
from database.helpers import visualization as viz

import pandas as pd

import statistics

if __name__ == '__main__':
    manager.setup_connection()


    algorithm_name = 'RandomForestRegressor-14'
    tickers = ['aa']
    evaluator = evaluator_adaptor.get_evaluator(algorithm_name)

    # Analysis
    evaluation_adaptor.test_evaluations(evaluator)



