from database.loaders.feature_sets import one
from database.adaptors import training_data as training_data_adaptor

import json

import pandas as pd

# -------------- load algorithm configurations -------------- #

config_file = open('algo_config.json')
config = json.load(config_file)
config_file.close()

# -------------- load features ------------------ #

data = pd.read_csv('training_data.csv')
one.load_features(data)

# -------------- Visualize feature data -------------- # 
