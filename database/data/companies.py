import mongoengine

class Company(mongoengine.Document):
    ticker = mongoengine.StringField(required=True, unique=True)
    company_name = mongoengine.StringField(required=True)
    industry = mongoengine.StringField(required=True)
    sector = mongoengine.StringField(required=True)

    

    meta = {
        'db_alias': 'core',
        'collection': 'companies',
    }

