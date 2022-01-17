import math

#help mathmatical function

def divide(num,dom):
    
    if dom == 0:
        return 0
    
    return num/dom

def normalize_to_percent(dict):
    total = sum(dict.values())
                
    normalized_dict = {}
    
    
    for feature in dict:
        normalized_dict[feature] = dict[feature] / total
        
    return normalized_dict

def normalize_features(features, means, stdevs):

    for i in range(features.shape[0]):
        for j in range(features.shape[1]):
            features[i][j] = (features[i][j] - means[j]) / stdevs[j]

    return features


