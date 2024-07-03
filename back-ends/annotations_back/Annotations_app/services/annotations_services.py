import datetime
import logging

from Annotations_app.db.annotationsdb import Annotationsdb
from Annotations_app.tenants.tenantservice import get_conn_config



class AnnotationsService:
    '''
    This class allows you to make queries to the databases, 
    by means of functions that perform the service functions, 
    for each query you want to create you must create a function
    '''

    def __init__(self, request=None):
        # configure connection
        self.create_connection(request)

    def __close__(self):
        self.db.close()

    def create_connection(self, request=None):

        config = get_conn_config(request)
        if not config:
            logging.error("Couldn't find database configuration", extra={'tenantId': 'None', 'code': 'VBA007'})
            raise Exception("ERROR: Couldn't find database configuration")

        options = None
        if 'OPTIONS' in config:
            if 'options' in config['OPTIONS']:
                options = config['OPTIONS']['options']

        db_conn = Annotationsdb(config,options)
        db_conn.connect()
        self.db = db_conn
        return db_conn

    def close(self):
        self.db.close()

    def commit(self):
        self.db.commit()


    '''Services queries''' 
    
    # Save annotations depends on user id 
    def save_annotations(self, data_annotations, user_id, version):
        
        for annotation in data_annotations:
            # replace fields values
            annotation['annotationVersion'] = version
            annotation['annotationCreatedBy'] = user_id
            annotation['annotationDateTime'] = datetime.datetime.utcnow()
            # remove view's _id
            if '_id' in annotation:
                annotation['_seq_id'] = annotation['_id']
                annotation.pop('_id', None)
        
        
        self.db.save_annotations(data_annotations)
        
        
        # Lambda is using for add data_annotations while map function is running
        return list(map(lambda x: self.format_annotation(x), data_annotations))
    

    # Get all annotations depends on version
    def get_annotations(self, study_id, list_versions):

        answer = { 'annotationVersions' : [] }

        for annotation_version in list_versions:

            version = annotation_version['version']
            annotation = self.db.get_annotations(study_id, version)
            annotation_list = list(map(lambda x: self.format_annotation(x), annotation))
            # create version data
            version_answer = {'annotationVersion':str(version), 'annotations':{} }
            
            # each version includes an annotation list
            for annot in annotation_list:
                annotation_id = annot['annotationId']

                if annotation_id:
                    version_answer['annotations'][annotation_id] = annot

            # append version data to answer
            answer['annotationVersions'].append(version_answer)

        return answer

    def get_all_versions(self, study_id):
        return self.db.get_all_versions(study_id)

    # Create all version for each annotation saved 
    def create_version(self, study_id, user_id):
        return self.db.create_version(study_id, user_id)
    
    def format_annotation(self, annotation):

        # set bd id as string
        id = annotation.get('_id')
        annotation['annotationId'] = str(id)
        
        # replace id with original sequence
        if '_seq_id' in annotation:
            annotation['_id'] = annotation['_seq_id']
        else:
            annotation.pop('_id', None)
            
        # convert version to string
        if 'annotationVersion' in annotation :
            annotation['annotationVersion'] = str(annotation['annotationVersion'])

            
        return annotation