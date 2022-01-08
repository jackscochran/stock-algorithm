import math

#help mathmatical function

def divide(num,dom):
    
    if dom == 0:
        return 0
    
    return num/dom

def normalize(dict):
    total = sum(dict.values())
                
    normalized_dict = {}
    
    
    for feature in dict:
        normalized_dict[feature] = dict[feature] / total
        
    return normalized_dict

