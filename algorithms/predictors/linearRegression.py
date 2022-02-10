import numpy as np
from sklearn.linear_model import LinearRegression

NAME = 'LinearRegressor'
RANDOM_GRID = None

def train(X, y):

    model = LinearRegression().fit(X, y)
    print(f'R^2: {model.score(X,y)}')
    return model

def evaluate(model, X):

    prediction = X.dot(model.coef_) + model.intercept_

    return max(0, prediction) # price cant fall below 0
 
def feature_analysis(model, features):
    return