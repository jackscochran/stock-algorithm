import mongoengine

def setup_connection():
    mongoengine.connect(db='algorithmPrototype', alias='core', host='localhost:27017')
    
