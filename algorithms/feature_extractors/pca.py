import numpy as np
from sklearn.decomposition import PCA

NAME = 'pca'

def extract(X, y, next_X):

    # create instance of PCA
    variance_kept = 0.9
    pca = PCA(variance_kept)

    transformed_X = pca.fit_transform(X)

    print(f'PCA reduced number of companents from {X.shape[1]} to {transformed_X.shape[1]}')

    return transformed_X, pca.transform(next_X)