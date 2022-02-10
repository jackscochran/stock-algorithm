import mongoengine

class MonthlyPrice(mongoengine.Document):
    # the average price for a company for a given month
    ticker = mongoengine.StringField(required=True)
    date = mongoengine.StringField(required=True)
    value = mongoengine.FloatField(required=True)

    meta = {
        'db_alias': 'core',
        'collection': 'monthly_prices',
        'indexes': [
            {'fields': ('ticker', 'date'), 'unique': True}
        ]
    }

class DailyPrice(mongoengine.Document):
    # the closing price of a company on a given date
    ticker = mongoengine.StringField(required=True)
    date = mongoengine.StringField(required=True)
    value = mongoengine.FloatField(required=True)

    meta = {
        'db_alias': 'core',
        'collection': 'daily_prices',
        'indexes': [
            {'fields': ('ticker', 'date'), 'unique': True}
        ]
    }
