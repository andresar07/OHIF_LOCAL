import logging
from django.apps import AppConfig
from django.conf import settings
from key_images_app.tenants.dbsettings import update_db_configs
from key_images_app.tenants.updateres import start_update
import os


class KeyImagesAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'key_images_app'

    def ready(self):
        # update resources associated with tenants
        try:
            if settings.UPDATE_RES_ON_START:
                logging.info (f"Updating resources  {str(os.getpid())}")
                update_db_configs()

            # start updating resources periodically
            if settings.RESOURCES_REFRESH_TIME and settings.RESOURCES_REFRESH_TIME > 0:
                start_update()

        except Exception as e:
            logging.error(f"Error Could not update tenant resources: {str(e)}", extra={'tenantId': 'None', 'code': 'VBK037'})
                
