import numpy as np
from sklearn.neural_network import MLPRegressor
from sklearn.model_selection import RandomizedSearchCV

import pprint


NAME = 'MLPRegressor'
RANDOM_GRID = {
    'hidden_layer_sizes': [(21,), (50), (21,21), (50,50), (21,21,21), (50,50,50)],
    'activation': ['tanh', 'relu'],
    'solver': ['sgd', 'adam'],
    'alpha': [0.0001, 0.05],
    'learning_rate': ['constant','adaptive'],
    'max_iter': [750]
}

def train(X, y):

    model = MLPRegressor()

    random_model = RandomizedSearchCV(
        estimator=model,
        param_distributions = RANDOM_GRID, 
        n_iter = 15, 
        cv = 3, 
        verbose=2, 
        random_state=42, 
        n_jobs = -1
    )

    random_model.fit(X, y)

    pprint.pprint(random_model.best_params_)
    print(f'Model Score: {random_model.score(X, y)}')

    return random_model

def evaluate(model, X):

    prediction = model.predict([X])

    return prediction[0]