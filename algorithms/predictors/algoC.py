from scipy.stats import stats as scipy_stats

NAME = 'AlgoC'
RANDOM_GRID = None
TRAINING_DATA = None

def train(X, y):

    model = []
    global TRAINING_DATA
    TRAINING_DATA = X

    # find correlations between each feature and the target variable

    for i in range(X.shape[1]):
        column = list(X[:,i])
        model.append(scipy_stats.pearsonr(column, list(y))[0])

    return model

def evaluate(model, X):

    # find what percentile the company is in for each variable

    for i in range(X.shape[0]):
        X[i] = sum(list(TRAINING_DATA[:,i]) < X[i]) / TRAINING_DATA.shape[0] 

    # evaluation is the product sum of a companies feature percentiels and the feature weightings 

    value = 0

    for i in range(len(model)):
        value += model[i] * X[i]

    return value

def feature_analysis(model, features):
    for i in range(len(model)):
        print('Variable: {:20} Correlation: {}'.format(*(features[i], model[i])))
