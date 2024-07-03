
import logging
import threading
import cachecontrol
import google.auth.transport.requests
import requests

from django.http import HttpResponse
from google.oauth2 import id_token
from django.conf import settings

from Annotations_app.tenants.dbsettings import get_tenant_id_from_auth_id
from pyGoogleAuthLib.google_identity_tools import GoogleIdentityUtils


# used for dbrouter. 
thread_Local = threading.local()

# checks access token
class GoogleAuthMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response
    

    def __call__(self, request):

        payload = validate_google_token(request)
        if not payload:
            # if no payload means token doesn't exists or couldn't be validated
            if settings.JWT_AUTH_ENABLED:
                logging.error('Could not validate authorization token.', extra={'tenantId': 'None', 'code': 'VBA002'})
                return HttpResponse('Not authorized', status=401)
        else:
            request.token_payload = payload            
            # gets tenant identification from token payload
            auth_tenant = payload['firebase'][f'{settings.NAME_VARIABLE_TENANT_GOOGLE}']
            # Get user id from token tenant
            user_id = payload['user_id']
            tenant_id = None
            if auth_tenant:
                # if registered, the tenant id in the token must have an equivalente application id
                tenant_id = get_tenant_id_from_auth_id(auth_tenant)
            
            if user_id:
                request.user_id = user_id

            if tenant_id and user_id:
                request.tenant_id = tenant_id
            else:
                # if True, the tenant must be registered to use this back-end
                if settings.ONLY_REG_TENANTS_REQUESTS:
                    logging.error('Could not get tenant_id from payload', extra={'tenantId': 'None', 'code': 'VBA005'})
                    return HttpResponse('Not authorized', status=401)                  

        response = self.get_response(request)
        return response


# Validate the Google Identity token 
def validate_google_token(request): 
    number_attempts = 2 #It is defined. If it is left burned in the method parameter it throws error
    cache_reused = None
    if not hasattr(GoogleIdentityUtils, 'validate_token_google'): # Create the function with close/cache only once outside the view controller
        GoogleIdentityUtils.validate_token_google = GoogleIdentityUtils.google_identity_utils_closure()
    return GoogleIdentityUtils.validate_token_google(request, cache_reused, number_attempts)


