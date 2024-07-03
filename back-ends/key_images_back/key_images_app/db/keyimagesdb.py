import logging
import psycopg
import urllib.parse
import datetime
import json
from psycopg import errors
from ..exceptions.DBExceptions import DBExceptions
from django.db import connections

class SQLError(Exception):
    pass

# Persistence 
class keyimagesdb:
    
    default_conf = None
    default_options = None

    def __init__(self, config, options=None):
        self.default_conf = config
        self.default_options = options

    def connect(self):

        # default database connection
        config = connections.databases['default']
        # no options by default
        options = None
        if self.default_conf:
            config = self.default_conf
        if self.default_options:
            options = self.default_options

        # make connection
        self.conn = psycopg.connect(
            host = config['HOST'], 
            port = config['PORT'], 
            dbname = config['NAME'], 
            user = config['USER'], 
            password = config['PASSWORD'],
            options = options    
        )


    def close(self):
        self.conn.close()

    def commit(self):
        self.conn.commit()

    def test(self):
        # create a cursor
        cur = self.conn.cursor()
        cur.execute('SELECT version()')
        # display the PostgreSQL database server version
        db_version = cur.fetchone()
        logging.info(f'PostgreSQL database version: {str(db_version)}')      
        # close the communication with the PostgreSQL
        cur.close()

    def store_keyimage(self,data):
        rowsAdded = 0
        data['timestamp'] = (datetime.datetime.now()).isoformat()
        cur = self.conn.cursor()
        backlayer = json.dumps(data['backlayer'])
        try: 
            values = ( 
                data['keyimage_id'], 
                data['patient_id'],
                data['study_id'],
                data['serie_name'],
                data['serie_id'],
                data['is_multiframe'],
                data['instance_id'],
                data['slice'],
                data['wado_uri'],
                data['timestamp'],
                data['is_fusion'],
                backlayer,
            )
            sql_str = """
                INSERT INTO keyimages (keyimageuid, patientid, studyuid, seriename, seriesuid, ismultiframe, instanceuid, slice, wadouri, timestamp, isfusion, backlayer) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            cur.execute(sql_str, values)
            #self.conn.commit()
            rowsAdded =  cur.rowcount
        except errors.lookup(UNIQUE_VIOLATION) as e:
            message = str(data['keyimage_id']) + "is duplicated key"
            logging.info (f'PG CODE {str(e.pgcode)}')
            logging.error (f'PG ERROR {str(e.pgerror)}', extra={'tenantId': 'None', 'code': 'VBK017'})
            logging.error (message, extra={'tenantId': 'None', 'code': 'VBK017'})
            self.conn.rollback()
            raise DBExceptions(message)
        except psycopg.Error as e:
            logging.info (f'PG CODE {str(e.pgcode)}')
            logging.error (f'PG ERROR {str(e.pgerror)}', extra={'tenantId': 'None', 'code': 'VBK017'})
            self.conn.rollback()
            raise SQLError('Save key image failed')
        cur.close()
        return rowsAdded

    def retrieve_keyimages(self,data):
        keyimages = []
        cur = self.conn.cursor()   
        id = data['patient_id']
        try:
            sql_query = """
                SELECT keyimageuid, patientid,studyuid, seriename, seriesuid, ismultiframe, instanceuid, slice, wadouri, isfusion, backlayer 
                FROM keyimages WHERE patientid = %s
            """
            cur.execute(sql_query, (id,))

            records = cur.fetchall()
            columnNames = [column[0] for column in cur.description]

            for record in records:
                keyimages.append( dict( zip( columnNames , record ) ) )
            
            #self.conn.commit()            
        except psycopg.Error as e:
            logging.info (f'PG CODE {str(e.pgcode)}')
            logging.error (f'PG ERROR {str(e.pgerror)}', extra={'tenantId': 'None', 'code': 'VBK017'})
            self.conn.rollback()
            raise SQLError('Retrieve key image failed')
        cur.close()
        return keyimages

    def delete_keyimage(self,key):
        rowsDeleted = 0
        cur = self.conn.cursor() 
        id = key
        try:
            sql_query = "DELETE FROM keyimages WHERE keyimageuid = %s"
            cur.execute(sql_query, (id,))
            #self.conn.commit()   
            rowsDeleted = cur.rowcount

        except psycopg.Error as e:
            logging.info (f'PG CODE {str(e.pgcode)}')
            logging.error (f'PG ERROR {str(e.pgerror)}', extra={'tenantId': 'None', 'code': 'VBK017'})
            self.conn.rollback()
            raise SQLError('Remove key image failed')
        
        cur.close()
        return rowsDeleted
