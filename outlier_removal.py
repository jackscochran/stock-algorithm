from database import manager 
from database.adaptors import training_data as training_data_adaptor

manager.setup_connection()
for point in training_data_adaptor.get_training_points(2):
    if point.target < -100:
        # other_point = training_data_adaptor.get_training_point(2, point.ticker, point.date)
        point.is_clean = False
        point.save()