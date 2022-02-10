from scipy.stats import stats as scipy_stats

NAME = 'AlgoCLinReg'
RANDOM_GRID = None

def train(X, y):

    model = []
    # find correlations between each feature and the target variable

    for i in range(X.shape[1]):
        column = list(X[:,i])
        slope, intercept, r, p, std_err = scipy_stats.linregress(column, list(y))

        model.append((r, slope, intercept, p))

    return model

def evaluate(model, X):
    
    value = 0
    for i in range(len(model)):
        value += model[i][0]*(model[i][1] * X[i] + model[i][2]) / model[i][3]

    return value

def feature_analysis(model, features):
    for i in range(len(model)):
        print('Variable: {:20} Correlation: {}'.format(*(features[i], model[i][0])))
