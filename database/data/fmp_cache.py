import mongoengine

class Response(mongoengine.Document):
    url = mongoengine.StringField(required=True, unique=True)
    results = mongoengine.ListField()

    meta = {
    'db_alias': 'core',
    'collection': 'fmp_cache'
    }


