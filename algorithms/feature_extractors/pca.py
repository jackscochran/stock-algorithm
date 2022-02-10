import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.model_selection import train_test_split

from sklearn import svm
from sklearn.metrics import roc_curve, auc
from sklearn.preprocessing import label_binarize
from sklearn.multiclass import OneVsRestClassifier
from scipy import interp
from sklearn.metrics import roc_auc_score
import matplotlib.pyplot as plt

df = pd.read_csv('training_data.csv')

features = ['Revenue USD Mil', 'Gross Margin %', 'Operating Income USD Mil', 'Operating Margin %',	'Net Income USD Mil','Earnings Per Share USD', 'Shares Mil', 'Book Value Per Share * USD', 'Operating Cash Flow USD Mil', 'Cap Spending USD Mil', 'Free Cash Flow USD Mil', 'Free Cash Flow Per Share * USD', 'Working Capital USD Mil', 'Asset Turnover (Average)', 'Return on Assets %', 'Financial Leverage (Average)', 'Return on Equity %', 'Return on Invested Capital %', 'Interest Coverage', 'Revenue % - Year over Year', 'Operating Income % - Year over Year', 'Net Income % - Year over Year', 'EPS % - Year over Year']

# seperate the features
df = df.loc[:, features + ['decision']]
df = df.dropna()
x = df.loc[:, features].values


# seperate out target
# threshold = 1.3
y = df.loc[:, ['decision']].values
print(y)
# split testing and training data
X_train, X_test, y_train, y_test = train_test_split(x, y, test_size=0.2)

# standardize features
scaler = StandardScaler()

# fit on training set only
scaler.fit(X_train)

# transform both train and test with train transform
X_train = scaler.transform(X_train)
X_test = scaler.transform(X_test)

# # create instance of PCA
# variance_kept = 0.8
# pca = PCA(variance_kept)

# pca.fit()

