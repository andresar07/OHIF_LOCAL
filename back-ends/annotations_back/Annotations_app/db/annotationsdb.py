from django.db import connections
from django.http import JsonResponse, HttpResponse

from psycopg.types.json import Json
import psycopg
import datetime
import logging

class SQLError(Exception):
    pass


class Annotationsdb:

    '''
    This class allows you to create functions to make queries of an exact type, 
    for each query you must establish a connection and make a commit.
    '''

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


    '''Queries functions'''
    def save_annotations(self, data_annotations):

        id_annotation_saved = []
        cur = self.conn.cursor()
        try:
            for annotation in data_annotations:
                number_slice = None
                total_slices = None
                if annotation['slice'] is not None:
                    temp_slice = annotation['slice'].split('/')
                    if len(temp_slice) > 1:
                        number_slice = int(temp_slice[0])
                        total_slices = int(temp_slice[1])
                
                sql_query = """
                    INSERT INTO annotation(annot_type, created_by, creation_date, data, instance_id, modality, series_id, slice, slices_number, study_id, title, parameters, version)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    RETURNING annot_id
                """
                values = (
                    annotation['annotationType'],
                    annotation['annotationCreatedBy'],
                    annotation['annotationDateTime'],
                    Json(annotation['data']),
                    annotation['instanceUid'],
                    annotation['modality'],
                    annotation['seriesUid'],
                    number_slice,
                    total_slices,
                    annotation['studyUid'],
                    annotation['annotationTitle'],
                    Json(annotation['annotationParameters']),
                    annotation['annotationVersion'],
                )
                cur.execute(sql_query, values)
                # Number position of annotation id
                annot_id = cur.fetchone()[0]

                id_annotation_saved.append(annot_id)

            # Commit all inserts
            self.conn.commit()
        except Exception as error:
            self.conn.rollback()
            print("SQL error", error)
            raise SQLError('Save annotations failed')

        finally:  
            cur.close()
        
        return id_annotation_saved
    
    
    def get_annotations(self, study_id, version):

        cur = self.conn.cursor()
        annotations = []

        try:
            sql_query = """
                SELECT annot_type, created_by, creation_date, data, instance_id, modality, series_id, slice, slices_number, study_id, title, parameters, version, annot_id
                FROM annotation
                WHERE study_id = %s AND version = %s
            """
            values = (
                study_id,
                version,
            )
            cur.execute(sql_query, values)
            results = cur.fetchall()

            if len(results) > 0:
                for row in results:
                    annotation = {}
                    annotation['annotationType'] = row[0]
                    annotation['annotationCreatedBy'] = row[1]
                    annotation['annotationDateTime'] = row[2]
                    annotation['data'] = row[3]
                    annotation['instanceUid'] = row[4]
                    annotation['modality'] = row[5]
                    annotation['seriesUid'] = row[6]
                    annotation['slice'] = str(row[7]) + '/' + str(row[8])
                    annotation['studyUid'] = row[9]
                    annotation['annotationTitle'] = row[10]
                    annotation['annotationParameters'] = row[11]
                    annotation['annotationVersion'] = row[12]                
                    annotation['_id'] = row[13]
                    annotations.append(annotation)

            self.conn.commit()
        except Exception as error:
            self.conn.rollback()
            print("SQL error", error)
            raise SQLError('Get annotations by version failed')           
        finally:
            cur.close()
        
        return annotations
        

    def create_version(self, study_id, user_id):

        last_version = self.get_last_version(study_id)
        current_version = last_version + 1

        cur = self.conn.cursor()

        try:
            # insert one annotation
            sql_query = """
                INSERT INTO annotation_version(study_id, version, created_by, creation_date)
                VALUES ( %s, %s, %s, %s)
            """
            values = (
                study_id, 
                current_version,
                user_id, 
                datetime.datetime.utcnow(),
            )

            cur.execute(sql_query, values)
            self.conn.commit()
        except Exception as error:
            self.conn.rollback()
            print("SQL error", error)
            raise SQLError('Create version failed')        
        finally:
            cur.close()
        
        return current_version
    


    def get_all_versions(self, study_id):

        cur = self.conn.cursor()
        list_versions = []

        try:
            sql_query = """
                SELECT version, created_by, creation_date FROM annotation_version
                WHERE study_id = %s
            """
            values = (
                study_id,
            )

            cur.execute(sql_query, values)
            result = cur.fetchall()
            
            if len(result) > 0:
                for row in result:
                    version = {}
                    version['studyUid'] = study_id
                    version['version'] = row[0] 
                    version['createdBy'] = row[1]
                    version['dateTime'] = row[2]                
                    list_versions.append(version)
            
            self.conn.commit()

        except Exception as error:
            self.conn.rollback()
            print("SQL error", error)
            raise SQLError('Get versions failed')
        finally:
            cur.close()
        
        return list_versions


    # get last version for given study
    def get_last_version(self, study_id):
        cur = self.conn.cursor()
        last_version = 0

        try:
            # Get max number of version column from the table 
            sql_query = """
                SELECT MAX(V.version) FROM "annotation" A, "annotation_version" V
                WHERE A.study_id = V.study_id and A.study_id = %s
            """
            values = (
                study_id,
            )
            
            cur.execute(sql_query, values)
            result = cur.fetchall()

            
            if result[0][0] is not None:
                last_version = result[0][0]
            
            self.conn.commit()
        except Exception as error:
            self.conn.rollback()
            print("SQL error", error)
            raise SQLError('Get version failed')
        finally: 
            cur.close()
        
        return last_version