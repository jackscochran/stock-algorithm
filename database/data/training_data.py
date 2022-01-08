import mongoengine

class TrainingSet(mongoengine.Document):
    idenifier = mongoengine.IntField(required=True, unique=True)
    feature_labels = mongoengine.ListField()

    meta = {
        'db_alias': 'core',
        'collection': 'training_sets'
    }

class TrainingPoint(mongoengine.Document):
    training_set_id = mongoengine.IntField(required=True)
    ticker = mongoengine.StringField()
    date = mongoengine.StringField(required=True)
    feature_values = mongoengine.ListField()
    target = mongoengine.FloatField()
    is_clean = mongoengine.BooleanField(required=True)

    meta = {
        'db_alias': 'core',
        'collection': 'training_points',
        'indexes': [
            {'fields': ('training_set_id', 'ticker', 'date'), 'unique': True}
        ]
    }
