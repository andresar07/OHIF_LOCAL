import logging
from django.db import connections
from django.conf import settings

from Annotations_app.tenants.dbsettings import get_tenant_db_name


header_name = 'Tenant-Name'


# gets database connection name
def get_tenant_db(tenant_id):
    db_name = get_tenant_db_name(tenant_id)
    if not db_name:
        db_name = 'default'
    return db_name


# tries to get the tenant Id from request
def get_tenant_from_request(request):
    if hasattr(request, 'tenant_id'):
        return request.tenant_id    
    return None    


# gets database configuration
def get_conn_config(request):

    # starts with default connection
    conn_config = connections.databases['default']
    if not request:
        # if no request use default configuration
        return conn_config
    

    # if there's a tenant use tenant connection
    tenant_id = get_tenant_from_request(request)
    if not tenant_id and settings.ONLY_REG_TENANTS_REQUESTS:
        logging.error('No tenant found in request', extra={'tenantId': 'None', 'code': 'VBA016'})
        raise Exception('ERROR: No tenant found in request')

    if tenant_id:
        # tenant -> use database for given tenant
        # db_key = get_tenant_db(tenant_id)
        # print("db_keyy ---------------> ", db_key)
        # if not db_key:
        #     print('ERROR: No database source found', tenant_id)
        #     raise Exception('ERROR: No database source found')
        
        # get database connection info using tenant id
        if tenant_id and tenant_id in connections.databases:
            conn_config = connections.databases[tenant_id]
        else:
            raise logging.error(f'No database source found, {str(tenant_id)}', extra={'tenantId': 'None', 'code': 'VBA017'})

    return conn_config


