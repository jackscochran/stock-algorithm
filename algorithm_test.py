
from database import manager
from database.adaptors import evaluators as evaluator_adaptor
from database.adaptors import evaluations as evaluation_adaptor
from database.adaptors import prices as price_adaptor
from database.adaptors import training_data as training_data_adaptor
from helpers import time
from database.helpers import plots

import pandas as pd

if __name__ == '__main__':
    manager.setup_connection()


    algorithm_name = 'DecisionTreeReg-1'
    tickers = ['aapl', 'tsla']
    evaluator = evaluator_adaptor.get_evaluator(algorithm_name)

    print(evaluation_adaptor.test_evaluations(evaluator))
    evaluation_adaptor.plot_predictions(evaluator, tickers)
    


