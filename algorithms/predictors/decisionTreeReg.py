import numpy as np
from sklearn.tree import DecisionTreeRegressor
from sklearn.model_selection import RandomizedSearchCV
import pprint

NAME = 'DecisionTreeRegressor'
RANDOM_GRID = {
    'max_features': ['sqrt'],
    'max_depth': [30], # was 30
    'min_samples_split': [5],
    'min_samples_leaf': [4]
    }

def train(X, y):

    model = DecisionTreeRegressor()
    random_model = RandomizedSearchCV(
        estimator=model,
        param_distributions = RANDOM_GRID, 
        n_iter = 1, 
        cv = 2, 
        verbose=2, 
        random_state=42, 
        n_jobs = -1
    )

    # fit model 
    random_model.fit(X, y)
    pprint.pprint(random_model.best_params_)
    print(f'Model Score: {random_model.score(X, y)}')


    return random_model

def evaluate(model, X):

    prediction = model.predict([X])

    return prediction[0]