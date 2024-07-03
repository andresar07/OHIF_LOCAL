import json
import logging

from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import api_view
from django.http import HttpResponseBadRequest, JsonResponse, HttpResponse

from Annotations_app.services.annotations_services import AnnotationsService


@swagger_auto_schema(
        method='GET',
        responses={200:'Http Response Annotations app'}
)
@api_view(['GET'])
def index(request):
    '''
    Endpoint to verify what is the API \n
        Type: GET request \n
        * Parameters: \n
            - request: HttpRequest to obtain data \n
        * Returns: \n
            - On validation success: Return message \n
    '''
    d = {'tenantId': 'Clinica-colsubsidio-r2iet', 'code': 'IV0001'}
    logging.debug('Entrando a la funcion de health.', extra=d)
    logging.info('Respuesta correcta', extra=d)
    logging.warning('No fue posible obtener la respuesta.')
    logging.error('No token.', extra=d)
    logging.critical('Servicio fatal error.')
    logging.warning('Protocol problem: ', extra=d)
    return HttpResponse('Annotations App!')


@swagger_auto_schema(
        method='GET',
        responses={200:'Http Response message ok'}
)
@api_view(['GET'])
def health(request):
    '''
    Endpoint to verify if the API is Ok \n
        Type: GET request \n
        * Parameters: \n
            - request: HttpRequest to obtain data \n
        * Returns: \n
            - On validation success: Return message \n
    '''
    return HttpResponse('Ok')



@swagger_auto_schema(
        method='POST',
        responses={400: 'Bad responses from function', 200:'Json response with result'}
)
@api_view(['POST'])
def save_new_annotation(request, study_id):
    '''
    Endpoint used to save annotation of study \n
        Type: POST request \n
        * Parameters: \n
            - request: HttpRequest to obtain data \n
            - study_id: Id of study \n
        * Returns: \n
            - On validation success: Return Json data of answer \n
            - On Validation failed: Return Json response with status 400 and notify error \n
    '''
    if request.method == 'POST':
        try:
            # get user id from request
            user_id = get_user_id(request)

            # get request data
            data_annotations = json.loads(request.body)['annotations']
            
            annotations_service = AnnotationsService(request)

            # Create version annotation
            version = annotations_service.create_version(study_id, user_id)
            annotations_saved = annotations_service.save_annotations(data_annotations, user_id, version)
            annotations_service.commit()
            annotations_service.close()

            answer = {       
                'version': str(version),
                'savedAnnotations': annotations_saved
            }
            
            return JsonResponse(answer)
        except Exception as error:
            logging.error(f"ERROR in save annotation study: {str(error)}", extra={'tenantId': 'None', 'code': 'VBA018'})
            return JsonResponse('ERROR in save annotation study: "%s"' % error, status=400)


@swagger_auto_schema(
        method='GET',
        responses={400: 'Bad responses from function', 200:'Json response with result'}
)
@api_view(['GET'])
def get_study_annotations(request, study_id):
    '''
    Endpoint used to obtain annotations studies \n
        Type: GET request \n
        * Parameters: \n
            - request: HttpRequest to obtain data \n
            - study_id: Id of study \n
        * Returns: \n
            - On validation success: Return Json data of result \n
            - On Validation failed: Return Json response with status 400 and notify error \n
    '''
    if request.method == 'GET':
        try:
            annotations_service = AnnotationsService(request)

            # Get all versions of annotations from study
            list_versions = annotations_service.get_all_versions(study_id)
            answer = annotations_service.get_annotations(study_id, list_versions)
            annotations_service.commit()
            annotations_service.close()

            return JsonResponse(answer)
        except Exception as error:
            logging.error(f"ERROR in get annotation study: {str(error)}", extra={'tenantId': 'None', 'code': 'VBA019'})
            return JsonResponse('ERROR in get annotation study: "%s"' % error, status=400)
        
        
# Get user id form request
def get_user_id(request):
    '''
    Return user_id saved before \n
        * Parameters: \n
            - request \n
        * Returns: \n
            - tenant_id: empty or tenant_id 
    '''
    # get tenant id if exists
    user_id = 'default_user'
    if hasattr(request, 'user_id'):
        user_id = request.user_id
    return user_id
