import mongoengine

class Evaluator(mongoengine.Document):
    key = mongoengine.StringField(required=True, unique=True) # algorithm-version
    config = mongoengine.DictField(required=True)

    meta = {
        'db_alias': 'core',
        'collection': 'evaluators'
    }