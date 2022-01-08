import mongoengine

class Evaluation(mongoengine.Document):
    ticker = mongoengine.StringField(required=True)
    evaluator_name = mongoengine.StringField(required=True)
    date = mongoengine.StringField(required=True)
    type = mongoengine.StringField(required=True)
    value = mongoengine.FloatField(requied=True)

    meta = {
        'db_alias': 'core',
        'indexes': [
            {'fields': ('ticker', 'date', 'evaluator_name'), 'unique': True}
        ]
    }
