import logging
from key_images_app.db.keyimagesdb import keyimagesdb
from key_images_app.tenants.tenantservice import get_conn_config
from django.db import connections

# this class allow to make queries to the database.
# It keeps a unique connection for all queries in transaction mode,
# if you want to make a each query in a single transaction, you should
# create an instance of this class for each query
class KeyImageService:
            
    def __init__(self, request=None):
        # configure connection
        self.create_connection(request)

    def __close__(self):
        self.db.close()

    def create_connection(self, request=None):

        config = get_conn_config(request)
        if not config:
            logging.error("Couldn't find database configuration", extra={'tenantId': 'None', 'code': 'VBK007'})
            raise Exception("ERROR: Couldn't find database configuration")

        options = None
        if 'OPTIONS' in config:
            if 'options' in config['OPTIONS']:
                options = config['OPTIONS']['options']

        db_conn = keyimagesdb(config,options)
        db_conn.connect()
        self.db = db_conn
        return db_conn

    def close(self):
        self.db.commit()
        self.db.close()

    def commit(self):
        self.db.commit()
        
    # stores the given key in database
    def store_keyimage(self, data):
        return self.db.store_keyimage(data)        
    
    # retrieves a list of key images for the given study
    def retrieve_keyimages(self, data):
        keyimages = self.db.retrieve_keyimages(data)
        return {"key_images": keyimages}

    # deletes the given key image from database
    def delete_keyimage(self, key):
        return self.db.delete_keyimage(key) 
