from database import manager 
from database.adaptors import training_data as training_data_adaptor

manager.setup_connection()
training_set_id = 2
training_set = training_data_adaptor.get_training_set(training_set_id)

for point in training_data_adaptor.get_training_points(training_set_id):
    if point.target > 100 or point.target < -100:
        # other_point = training_data_adaptor.get_training_point(2, point.ticker, point.date)
        point.is_clean = False
        

    # remove desiered features
    # features_to_remove = ['']
    # if len(point.feature_values) == len(training_set.feature_labels):
    #     for feature in features_to_remove: 
    #         point.feature_values.pop(training_set.feature_labels.index(feature))


    point.save()

# remove desiered feature labels
# for feature in features_to_remove:
#     training_set.feature_labels.remove(feature)
#     training_set.save()