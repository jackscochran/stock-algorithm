import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import RandomizedSearchCV
import pprint

NAME = 'RandomForestRegressor'
RANDOM_GRID = {
    'n_estimators': [400],
    'max_features': ['sqrt'],
    'max_depth': [30],
    'min_samples_split': [5],
    'min_samples_leaf': [4],
    'bootstrap': [True],
    }

def train(X, y):

    model = RandomForestRegressor()
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

def feature_analysis(model, features):
     # Get numerical feature importances, sort and display
    importances = list(model.best_estimator_.feature_importances_)
    feature_importances = [(feature, round(importance, 2)) for feature, importance in zip(features, importances)]
    feature_importances = sorted(feature_importances, key = lambda x: x[1], reverse = True)
    [print('Variable: {:20} Importance: {}'.format(*pair)) for pair in feature_importances]

