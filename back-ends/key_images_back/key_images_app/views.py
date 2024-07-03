import logging
from django.http import HttpResponse
from rest_framework.decorators import api_view
from django.http import JsonResponse
from django.http import HttpResponseBadRequest
from django.conf import settings
import json

from key_images_app.exceptions.DBExceptions import DBExceptions 
from key_images_app.services.keyimage_service import KeyImageService
from key_images_app.tenants.dbsettings import update_db_configs
from drf_yasg.utils import swagger_auto_schema


# default end point
@api_view(['GET'])
def index(request):
    d = {'tenantId': 'Clinica-colsubsidio-r2iet', 'code': 'IV0001'}
    logging.debug('Entrando a la funcion de health.', extra=d)
    logging.info('Respuesta correcta', extra=d)
    logging.warning('No fue posible obtener la respuesta.')
    logging.error('No token.', extra=d)
    logging.critical('Servicio fatal error.')
    logging.warning('Protocol problem: ', extra=d)
    return  HttpResponse('Key Images App!')


# health end point. It is used to check service availability
@swagger_auto_schema(method='get', responses={ "200":"OK", "401":"Unauthorized error"} )
@api_view(['GET'])
def health(request):
    return  HttpResponse('OK')


# stores a key image in the database. The payload must be a json object with an Id (keyimage_id attribute) 
# and all the data required by the viewer to open an instance inside a viewport (cell data)
@swagger_auto_schema(method='put', responses={ "200":"OK", "400": "Error storing data", "401":"Unauthorized error"})
@api_view(['PUT'])
def store(request):
    '''
    This endpoint stores a key image in the database. \n

    The payload must be a json object with an Id 
    and all the data required by the viewer to open an instance inside a viewport (cell data) \n
        Type: PUT \n
        Parameters: None
        Body:
            - Json with: 
                study_id, serie_name, serie_id, instance_id, wado_uri, is_fusion, 
                is_multiframe, patient_id, n_studies, keyimage_id
        Returns:    
            - On success: Json with number of rows added (added attribute)
            - On failed: Error 400
            - On token validation error: Error 401
    '''
    key_img_service = None
    try:
        data = json.loads(request.body)
        key_img_service = KeyImageService(request)
        rowsAdded = key_img_service.store_keyimage(data)
        answer = {'added': rowsAdded}
        key_img_service.commit()
        key_img_service.close()
        return  JsonResponse(answer)
    except Exception as e:
        logging.error(f"Could not store key image  {str(e)}", extra={'tenantId': 'None', 'code': 'VBK018'})
        if key_img_service:
            key_img_service.close()
        return HttpResponseBadRequest("ERROR: could not store key image")


# retrieves a list of all stored key images for a given patient. The payload
# must be a json object with the attribute "patient_id"
@swagger_auto_schema(method='post', responses={ "200":"OK", "400": "Error storing data", "401":"Unauthorized error"})
@api_view(['POST'])
def retrieve(request):
    '''
    It retrieves a list of all stored key images for a given patient.\n

    The payload must be a json object with the attribute "patient_id" \n
        Type: POST \n
        Parameters: None
        Body:
            - Json with: patient_id attribute
        Returns:    
            - On success: Json with all the key images stored for the given patient
            - On failed: Error 400
            - On token validation error: Error 401
    '''
    key_img_service = None
    try:
        data = json.loads(request.body) 
        key_img_service = KeyImageService(request)
        answer = key_img_service.retrieve_keyimages(data)
        key_img_service.commit()
        key_img_service.close()
        return JsonResponse(answer)
    except Exception as e:
        logging.error(f"Could not retrieve key image  {str(e)}", extra={'tenantId': 'None', 'code': 'VBK019'})
        if key_img_service:
            key_img_service.close()
        return HttpResponseBadRequest("ERROR: could not retrieve key image")


# removes a previously stored key image. The key parameter corresponds to the Id used
# when the image was stored
@swagger_auto_schema(method='delete', responses={ "200":"OK", "400": "Error storing data", "401":"Unauthorized error"})
@api_view(['DELETE'])
def delete(request,key):
    '''
    It removes a previously stored key image. \n

    The key parameter corresponds to the Id used
    when the image was stored \n
        Type: DELETE \n
        Parameters: 
            - key: Id of the Key Image to be removed
        Body: None
        Returns:    
            - On success: Json with the number of rows deleted from database
            - On failed: Error 400
            - On token validation error: Error 401
    '''
    key_img_service = None
    try:
        key_img_service = KeyImageService(request)
        rowsDeleted = key_img_service.delete_keyimage(key)
        answer = {'deleted': rowsDeleted}
        key_img_service.commit()
        key_img_service.close()
        return  JsonResponse(answer)
    except Exception as e:
        logging.error(f"Could not delete key image  {str(e)}", extra={'tenantId': 'None', 'code': 'VBK020'})
        if key_img_service:
            key_img_service.close()
        return HttpResponseBadRequest("ERROR: could not delete key image")
