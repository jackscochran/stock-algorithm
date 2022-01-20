import mongoengine

class Company(mongoengine.Document):
    ticker = mongoengine.StringField(required=True, unique=True)
    profile = mongoengine.DictField()


    meta = {
        'db_alias': 'core',
        'collection': 'companies',
    }

