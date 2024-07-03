import logging
import threading
import cachecontrol
import google.auth.transport.requests
import requests

from django.http import HttpResponse
from google.oauth2 import id_token
from django.conf import settings

from Annotations_app.tenants.dbsettings import get_tenant_id_from_auth_id

# used for dbrouter. 
# TODO: dbrouter is currently not used. Should remove this?
thread_Local = threading.local()

# checks access token
class AuthMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        session = requests.session()
        self.cached_session = cachecontrol.CacheControl(session)

    def __call__(self, request):
        # True -> check authorization token validity
        if settings.JWT_AUTH_ENABLED:
            try:
                token = None

                if settings.JWT_TOKEN_SOURCE == 'header':
                    # gets token from header
                    auth_header = request.headers['Authorization']
                    if not auth_header:
                        auth_header = request.headers['authorization']
                    if not auth_header:
                        auth_header = request.headers['AUTHORIZATION']
                    if not auth_header:
                        raise Exception ('ERROR: Authorization header is mandatory')
                    # token must be after "Bearer" word
                    str_tokens = auth_header.split(' ')
                    token = str_tokens[1].strip()

                if settings.JWT_TOKEN_SOURCE.startswith('cookie'):
                        # gets token from cookie
                        str_tokens = settings.JWT_TOKEN_SOURCE.split(":")
                        if len(str_tokens) == 2:
                            cookie_name = str_tokens[1].strip()
                            token = request.COOKIES.get(cookie_name) 

                if not token:
                    raise logging.error('Authorization token is mandatory', extra={'tenantId': 'None', 'code': 'VBA001'})

                tenant_id, user_id = self.validate_auth_token(token)

                if tenant_id:
                    request.tenant_id = tenant_id

                if user_id:
                    request.user_id = user_id

            except Exception as e:                
                logging.error(f'Could not validate authorization token. {str(e)}', extra={'tenantId': 'None', 'code': 'VBA002'})
                return HttpResponse('Not authorized', status=401)

        response = self.get_response(request)
        return response


    # validates the authorization token
    def validate_auth_token(self, token):
        # validates the token and get its payload
        auth_request = google.auth.transport.requests.Request(session=self.cached_session)
        firebase_id = 'deep-district-406416'
        id_info = id_token.verify_firebase_token(token, auth_request, firebase_id)

        # gets tenant identification from token payload
        auth_tenant = id_info['firebase']['tenant']
        tenant_id = None
        if auth_tenant:
            # if registered, the tenant id in the token must have an equivalente application id
            tenant_id = get_tenant_id_from_auth_id(auth_tenant)

        if tenant_id:
            setattr(thread_Local, "tenant_id", tenant_id)
        

        # Get user id from token tenant
        user_id = id_info['user_id']

        if user_id:
            setattr(thread_Local, "user_id", user_id)


        # if True, the tenant must be registered to use this back-end
        if settings.ONLY_REG_TENANTS_REQUESTS:
            if not auth_tenant:
                logging.error('No tenant information found.', extra={'tenantId': 'None', 'code': 'VBA003'})
                raise Exception ('ERROR: No tenant information found')
            if not tenant_id:
                logging.error(f'Tenant not registered: {str(tenant_id)}', extra={'tenantId': 'None', 'code': 'VBA004'})
                raise Exception ('ERROR: Tenant not registered: ', tenant_id)
            if not user_id:
                raise logging.error(f'Tenant no registred user id')
                
        
        return tenant_id, user_id


# returns the current tenant_id (the one extracted from request)
def get_request_tenant_id():
    return getattr(thread_Local, "tenant_id", None)
