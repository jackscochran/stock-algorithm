
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


    algorithm_name = 'AlgoCLinReg-8'
    tickers = ['aa']
    evaluator = evaluator_adaptor.get_evaluator(algorithm_name)

    # plot evaluator returns over time
    universe = {}
    top1 = {}
    top5 = {}   
    bottom1 = {}
    bottom5={}


    # current_date = evaluator.config['train_start']
    # while current_date <= evaluator.config['train_end']:
    #     print(f'Calculating Returns for {current_date}')
    #     evals = list(evaluation_adaptor.get_top_evaluations_by_date(algorithm_name, current_date))

    #     if len(evals) > 0:
    #         # universe[current_date] = statistics.median(training_data_adaptor.get_training_point(evaluator.config['training_set_id'], evals[i].ticker, current_date).target for i in range((len(evals))))
    #         top1[current_date] = statistics.median(training_data_adaptor.get_training_point(evaluator.config['training_set_id'], evals[i].ticker, current_date).target for i in range(int(len(evals)*0.01)))
    #         top5[current_date] = statistics.median(training_data_adaptor.get_training_point(evaluator.config['training_set_id'], evals[i].ticker, current_date).target for i in range(int(len(evals)*0.05)))
    #         bottom1[current_date] = statistics.median(training_data_adaptor.get_training_point(evaluator.config['training_set_id'], evals[len(evals) - i - 1].ticker, current_date).target for i in range(int(len(evals)*0.01)))
    #         bottom5[current_date] = statistics.median(training_data_adaptor.get_training_point(evaluator.config['training_set_id'], evals[len(evals) - i - 1].ticker, current_date).target for i in range(int(len(evals)*0.05)))

    #     current_date = time.get_months_ahead(current_date, evaluator.config['holding_period']) 

    # viz.df_bar(pd.DataFrame({
    #     'Top 1%': [avg for avg in top1.values()],
    #     'Top 5%': [avg for avg in top5.values()],
    #     'Bottom 1%': [avg for avg in bottom1.values()],
    #     'Bottom 5%': [avg for avg in bottom5.values()]
    #     # 'Data Set Average': [avg for avg in universe.values()]
    # }), legend_title='Comparisons')

    # Analysis
    evaluation_adaptor.test_evaluations(evaluator)



    # evaluation_adaptor.sample_predictions(evaluator, tickers)
    # 



