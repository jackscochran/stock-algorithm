import numpy as np
from sklearn.tree import DecisionTreeRegressor

NAME = 'DecisionTreeReg'

def train(X, y):

    model = DecisionTreeRegressor().fit(X, y)
    return model

def evaluate(model, X):

    prediction = model.predict([X])

    return max(0, prediction[0]) # price cant fall below 0