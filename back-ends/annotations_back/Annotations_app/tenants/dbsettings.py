import logging
from django.db import connections
from django.conf import settings
from django.core.management import call_command

from Annotations_app.utils.th_lock import th_lock
from threading import Timer
import requests

import psycopg

# lock on maps to avoid concurrent writes
map_lock = th_lock()

# map of db connectios used by each tenant
_db_tenants_map:map = {
}

# keeps all the database connections used by this app
_db_map:map = {
}

# authenticator id - tenant id relation
_auth_tenants_map:map = {
}


DB_ENGINE = 'django.db.backends.postgresql'
TENANT_RESOURCE_URI = 'tenant/resource'
RESOURCE_TENANTS_URI = 'tenant/list/resource'
ALL_RESOURCES_BY_TYPE_URI = 'tenant/list/resource/type'
RESOURCE_TYPE = settings.RESOURCE_TYPE

def get_db_map():
    return _db_map

def get_db_tenants_map():
    return _db_tenants_map

def get_auth_tenants_map():
    return _auth_tenants_map

# get the tenant identifier associated to the given authentication id
def get_tenant_id_from_auth_id(auth_id):
    auth_tenants_map = get_auth_tenants_map()
    if auth_id in auth_tenants_map:
        return auth_tenants_map[auth_id]
    return None

# get the name of the database associated to the given tenant
def get_tenant_db_name(tenant_id):
    db_tenants_map = get_db_tenants_map()
    if tenant_id in db_tenants_map:
        return db_tenants_map[tenant_id]
    return None

# formats the database source configuration as expected by django "connections" 
def get_config_from_resource_data(resource_data):

    # values are mandatory
    if not resource_data['db_name'] or not resource_data['host_name'] or not resource_data['port']:
        logging.error(f"No database resource data found: {str(resource_data)}", extra={'tenantId': 'None', 'code': 'VBA008'})
        raise Exception("ERROR: No database resource data found")

    # TODO: decrypt ??
    # TODO: default on missing values
    config = {
        'ENGINE': DB_ENGINE,
        'NAME': resource_data['db_name'],
        'USER': resource_data['user_name'],
        'PASSWORD': resource_data['password'],
        'HOST': resource_data['host_name'],
        'PORT': resource_data['port'],
        'ATOMIC_REQUESTS': False, 
        'AUTOCOMMIT': True, 
        'CONN_MAX_AGE': 0,
        'CONN_HEALTH_CHECKS': False,
        'OPTIONS': {}, 
        'TIME_ZONE': None,
        'TEST': {'CHARSET': None, 'COLLATION': None, 'NAME': None, 'MIRROR': None, 'MIGRATE': True}      
    }
    return config


# makes requests to tenant management service and updates the internal
# db maps (db_map variable). The previous value of db_map is discarded
def check_tenant_resources():

    tmp_db_map = None
    resources_ids = settings.TENANT_RESOURCES
    if resources_ids and len(resources_ids) > 0:
        # get resources. Resources are db connections
        tmp_db_map = get_resources(resources_ids)
    else:
        tmp_db_map = get_all_resources()

    if tmp_db_map:
        # lock maps for writing 
        map_lock.start_loading()
        global _db_map
        _db_map = tmp_db_map
        # unlock maps
        map_lock.end_loading()


# Get all resources_id and your resources depends on type resource
def get_all_resources():

    tenants_url = settings.TENANT_BASE_URL
    if tenants_url.endswith("/"):
        tenants_url = tenants_url[:-1]

    tmp_db_map = {}
    url = f'{tenants_url}/{ALL_RESOURCES_BY_TYPE_URI}/{RESOURCE_TYPE}'
    
    # makes a sync request to get configuration for resource
    try:
        r = requests.get(url)
        resource_list = r.json()

        if not resource_list:
            raise logging.error("Can not get resources", extra={'tenantId': 'None', 'code': 'VBA009'})

        for resource_id in resource_list:
            
            config = get_config_from_resource_data(resource_list[resource_id]['config'])

            if config:
                tmp_db_map[resource_id] = config

            if not config:
                logging.error (f"Can not add config to resource: {str(resource_id)}", extra={'tenantId': 'None', 'code': 'VBA010'})

    except Exception as e:                
        logging.error (f"Couldn't gets resource of type: {str(RESOURCE_TYPE)}", extra={'tenantId': 'None', 'code': 'VBA011'})
        logging.debug (f"Exception: {str(e)}")

    return tmp_db_map


# Get all resources_id and your resources 
def get_resources(resources_ids):

    tenants_url = settings.TENANT_BASE_URL
    if tenants_url.endswith("/"):
        tenants_url = tenants_url[:-1]

    tmp_db_map = {}
    if not resources_ids or len(resources_ids) == 0:
        logging.warning ("No resources defined, using default resource")
    else:
        # traverses all resources and request database connection data
        for resource_id in resources_ids:            
            url = f'{tenants_url}/{TENANT_RESOURCE_URI}/{resource_id}'
            # makes a sync request to get configuration for resource
            try:
                r = requests.get(url)
                resource_data = r.json()
                config = None
                if resource_id in resource_data:
                    config = get_config_from_resource_data(resource_data[resource_id]['config'])
                    if config:
                        tmp_db_map[resource_id] = config

                if not config:
                    logging.error (f"Resource was not found: {str(resource_id)}", extra={'tenantId': 'None', 'code': 'VBA012'})

            except Exception as e:                
                logging.error (f"Couldn't get resource data. Resource Id: {str(resource_id)}", extra={'tenantId': 'None', 'code': 'VBA013'})
                logging.debug (f"Exception: {str(e)}")

    return tmp_db_map


# gets all the tenants that will be redirected to each resource and keeps this information
# in db_tenants_map. The previous value of the map is discared
def check_tenants(resources_ids):
    
    tenants_url = settings.TENANT_BASE_URL
    if tenants_url.endswith("/"):
        tenants_url = tenants_url[:-1]
    
    if not resources_ids or len(resources_ids) == 0:
        logging.warning ("No resources defined, using default resource")
    else:
        # traverses all resources and request tenants list
        tmp_auth_tenants_map = {}
        tmp_db_tenants_map = {}
        for resource_id in resources_ids:            
            url = f'{tenants_url}/{RESOURCE_TENANTS_URI}/{resource_id}'
            # makes a sync request to get configuration for resource
            try:
                r = requests.get(url)
                resource_data = r.json()
                if not resource_data or len(resource_data['tenants']) == 0:
                    logging.warning  (f"There are no tenants for the resoruce: {str(resource_id)}")
                else:
                    for tenant in resource_data['tenants']:
                        auth_id = tenant['auth_id'].strip()
                        tenant_id = tenant['tenant_id'].strip()
                        if auth_id in tmp_auth_tenants_map:
                            # if id is already registered, check that tenat is the same. One authentication
                            # id must correspond to one tenant
                            if tmp_auth_tenants_map[auth_id] != tenant_id:
                                logging.error(f"Authentication id already associated to another tenant. Will be discarded. {str(auth_id)}", extra={'tenantId': 'None', 'code': 'VBA014'})

                        # registers authentication id
                        tmp_auth_tenants_map[auth_id] = tenant_id
                        if tenant_id in tmp_db_tenants_map:
                            if tmp_db_tenants_map[tenant_id] != resource_id:
                                logging.error(f"Tenant Id with more than one resource: {str(tenant_id)}", extra={'tenantId': 'None', 'code': 'VBA015'})
                                raise Exception(f"Tenant Id with more than one resource: {str(tenant_id)}")
                        
                        # associates tenant to database resource
                        tmp_db_tenants_map[tenant_id] = resource_id

            except Exception as e:                
                logging.error (f"Couldn't get resource tenants. Resource Id: {str(resource_id)}", extra={'tenantId': 'None', 'code': 'VBA006'})
                logging.debug (f"Exception: {str(e)}")

        # gets lock on maps before writing them
        map_lock.start_loading()

        # replace current maps
        global _auth_tenants_map
        global _db_tenants_map
        _auth_tenants_map = tmp_auth_tenants_map
        _db_tenants_map = tmp_db_tenants_map
        logging.info( f"Tenants  {str(_auth_tenants_map)}")
        logging.info( f"Resources {str(_db_tenants_map)}")

        # release lock
        map_lock.end_loading()


# updates django database connections
def update_db_configs(do_migration=True):

    # gets database sources
    check_tenant_resources()
    resource_ids = []
    db_map = get_db_map()
    if db_map:
        resource_ids = list(db_map.keys())
    # update the db_tenants_map
    check_tenants(resource_ids)

    logging.info ("Start updating database sources")
    db_tenants_map = get_db_tenants_map()

    # creates a new database connection for each tenant
    for tenant_id in db_tenants_map:
        # db name is resource id of tenant
        db_name = db_tenants_map[tenant_id]
        # check if database data exists, because resource id is the key of config database
        if db_name in db_map:
            # creates a new connetion data with tenant as scheme
            tenant_connection = db_map[db_name].copy()
            tenant_connection['OPTIONS'] = {
                'options': '-c search_path='+tenant_id
            }
            # User tenant_id like to key for save configuration of the connection 
            connections.databases[tenant_id] = tenant_connection
        else:
            # maybe tenant want to use default database
            if db_name == 'default':
                # creates a new connetion data with tenant as scheme
                tenant_connection = connections.databases[db_name].copy()
                tenant_connection['OPTIONS'] = {
                    'options': '-c search_path='+tenant_id
                }
                connections.databases[tenant_id] = tenant_connection                
            else:
                logging.warning(f"No database source with name: {str(db_name)}")

        if not check_list_schemas(tenant_id):
            # try to create scheme and tables for new tenant
            create_schema(tenant_id)
            # migrate tables
            make_migration(tenant_id)

    logging.info ("Update finished")


# Gets the list of schemas that currently exist in the database  
def check_list_schemas(tenant_id):

    found = False
    config = connections.databases[tenant_id]
    if config:
        conn = psycopg.connect(
            host = config['HOST'], 
            port = config['PORT'], 
            dbname = config['NAME'], 
            user = config['USER'], 
            password = config['PASSWORD'] 
        )

        try:
            with conn.cursor() as cursor:

                sql_str = """
                    SELECT schema_name 
                    FROM information_schema.schemata;
                """
                cursor.execute(sql_str)
                record = cursor.fetchall()
                for data in record:
                    old_tenant_id = data[0].upper()
                    id = tenant_id.upper()
                    if id == old_tenant_id:
                        found = True
                        break

                conn.commit()

        except Exception as error:
            print("ERROR in get list of schemas from  database: ", error)

        conn.close()
        return found


# Tries to create a new schme on the database associated to the given tenant
def create_schema(tenant_id):
    config = connections.databases[tenant_id]
    if config:
        conn = None
        try:
            conn = psycopg.connect(
                host = config['HOST'], 
                port = config['PORT'], 
                dbname = config['NAME'], 
                user = config['USER'], 
                password = config['PASSWORD'],
            )
            user = config['USER']
            with conn.cursor() as cursor:
                cursor.execute( f"CREATE SCHEMA IF NOT EXISTS {tenant_id}" )
                cursor.execute( f"GRANT ALL ON schema {tenant_id} TO {user}" )
                conn.commit()
        except Exception as e:
            print ("Scheme not created ", e)

        if conn:
            conn.close()


# Tries to migrate entities to the database for the given tenant
def make_migration(tenant_id):
    config = connections.databases[tenant_id]
    if config:
        try:
            call_command("migrate", database=tenant_id, interactive=False, skip_checks=False)
        except Exception as e:
            print ("Migration error ", e)


