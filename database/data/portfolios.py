import mongoengine

class Portfolio(mongoengine.Document):
    algorithm = mongoengine.StringField(required=True)
    start_date = mongoengine.StringField(required=True)
    end_date = mongoengine.StringField(required=True)
    holding_period = mongoengine.FloatField(required=True)
    trade_load = mongoengine.FloatField(required=True)
    trade_period = mongoengine.FloatField(required=True)
    lookback = mongoengine.FloatField(required=True)

    trades = mongoengine.DictField(required=True)
    balances = mongoengine.DictField(required=True)
    metrics = mongoengine.DictField(required=True)

    meta = {
        'db_alias': 'core',
        'collection': 'portfolios',
        'indexes': [
            {
                'fields': (
                    'algorithm', 
                    'start_date', 
                    'end_date', 
                    'holding_period',
                    'trade_load',
                    'trade_period',
                    'lookback'
                    ), 
                'unique': True
            }
        ]
    }