import logging
import os
from django.apps import AppConfig
from django.conf import settings

from Annotations_app.tenants.dbsettings import update_db_configs
from Annotations_app.tenants.updateres import start_update

class AnnotationsAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'Annotations_app'

    def ready(self):
        try:
            if settings.UPDATE_RES_ON_START:
                logging.info (f"Updating resources  {str(os.getpid())}")
                update_db_configs()

            # start updating resources periodically
            if settings.RESOURCES_REFRESH_TIME and settings.RESOURCES_REFRESH_TIME > 0:
                start_update()

        except Exception as error:
            logging.error(f"Error Could not update tenant resources: {str(error)}", extra={'tenantId': 'None', 'code': 'VBA037'})  
            raise Exception ("ERROr: Could not update tenant resources")
                