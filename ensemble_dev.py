from database.adaptors import portfolios as portfolio_adaptor
from database import manager

# from database.adaptors import evaluations as evaluation_adaptor
# from database.adaptors import evaluators as evaluator_adaptor
# from database import manager
# import statistics

# algorithms = ['AlgoCLinReg-2', 'RandomForestRegressor-2']
# threshold_date = '2022-10'
# algorithm_name = '-'.join(algorithms)
# manager.setup_connection()
# evaluator = evaluator_adaptor.get_evaluator(algorithm_name)
# if evaluator is None:
#     evaluator = evaluator_adaptor.add_evaluator(
#         {
#             'name': algorithm_name,
#             'version': '',
#             'output_type': 'relative_return'
#         }
#     )

# for evaluation in evaluation_adaptor.get_all_evaluations(algorithms[1]): # use 1st algorithm as driver
#     if evaluation.date < threshold_date:
#         continue
#     predictions = []
#     predictions.append(evaluation.value)
#     for i in range(1, len(algorithms)):
#         prediction = evaluation_adaptor.get_evaluation(algorithms[i], evaluation.ticker, evaluation.date)
#         if prediction is not None:
#             predictions.append(prediction.value)

#     if len(predictions)==len(algorithms):
#         print(evaluation.date)
#         evaluation_adaptor.add_evaluation(
#             evaluation.ticker, 
#             evaluation.type, 
#             algorithm_name, 
#             evaluation.date, 
#             statistics.mean(predictions)
#         )