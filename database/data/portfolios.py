import mongoengine

class Portfolio(mongoengine.Document):
    creator = mongoengine.StringField(required=True)
    start_date = mongoengine.StringField()
    end_date = mongoengine.StringField()
    trades = mongoengine.DictField()
    balances = mongoengine.DictField()
    metrics = mongoengine.DictField()

    meta = {
        'db_alias': 'core',
        'collection': 'portfolios'
    }