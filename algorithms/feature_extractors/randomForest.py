import numpy as np
from sklearn.ensemble import RandomForestRegressor

NAME = 'randomForest'

def extract(X, y, next_X):
    # extract features using rf
    rf = RandomForestRegressor(
        n_estimators = 150,
        max_features = 'sqrt',
        max_depth = None,
        min_samples_split = 2,
        min_samples_leaf = 24,
        bootstrap = True
    )

    rf.fit(X, y)
    importances = list(rf.feature_importances_)
    to_delete = []

    for i in range(len(importances)):
        if importances[i] < 0.03:
            to_delete.append(i)

    print(f'Deleted Columns: {to_delete}')

    return np.delete(X, to_delete, axis=1), np.delete(next_X, to_delete, axis=1) # something that can map