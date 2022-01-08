from ..database.adaptors import ratings
from ..database.adaptors import training_data


def rate(ticker, date, weightings, percentile_period):
    features = get_feature_values(ticker, date)
        
    percentiles = get_percentiles(features, date, percentile_period)
    
    rating = 0
    
    for feature in features:
        rating += percentiles[feature]*weightings[feature]
    
    return rating

def get_percentiles(features, date, period):
    
    feature_data = []
    
    for company in TrainingCompany.objects(date__lte=date, date__gte=get_months_ahead(date, -12*period)):
        feature_data.append(company)
        
        
    percentiles = {}
    # initalize percentile dict
    for feature in features:
        percentiles[feature] = 0
    
    for company in feature_data:
        company_features = get_feature_dict(company)
        for feature in features:
            if company_features[feature] > features[feature]:
                percentiles[feature] += 1
                
    # convert to %
    total = len(feature_data)
    
    for feature in percentiles:
        percentiles[feature] = 1- percentiles[feature]/total
                
    return percentiles

def load_ratings_by_month(start_date, end_date):
    
    current_date = start_date
    
    while(True):
        if current_date > end_date:
            return
        
        training_companies = TrainingCompany.objects(date=current_date)
        
        print('\n-----------------')
        print(current_date)

        training_years = 2
        percentile_years = 2
        
        x, y = get_training_data(get_months_ahead(current_date, training_years * -12), current_date)
        weightings = r_model(x,y)
        
        for company in training_companies:
            company = Company.objects(ticker=company.ticker).first()
            get_rating(company.ticker, current_date, weightings, percentile_years)
            print(company.ticker)
        
        current_date = get_months_ahead(current_date, 1)

