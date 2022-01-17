import numpy as np
from sklearn.ensemble import RandomForestRegressor

NAME = 'RandomForestRegressor'

def train(X, y):

    model = RandomForestRegressor(
        min_samples_split= 5,
        min_samples_leaf = 4,
        max_features = 'sqrt',
        max_depth=30
    ).fit(X, y)

    return model

def evaluate(model, X):

    prediction = model.predict([X])

    return prediction[0]