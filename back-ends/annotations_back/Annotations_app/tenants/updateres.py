import time
from timeloop import Timeloop
from datetime import timedelta

from Annotations_app.tenants.dbsettings import update_db_configs
from django.conf import settings

tl = Timeloop()

RESOURCES_REFRESH_TIME = settings.RESOURCES_REFRESH_TIME

# set default value
if not RESOURCES_REFRESH_TIME or RESOURCES_REFRESH_TIME <= 0:
    RESOURCES_REFRESH_TIME = 60 

# called periodically to update resources and tenants
@tl.job(interval=timedelta(seconds=RESOURCES_REFRESH_TIME))
def refresh_tenant_resources():
    update_db_configs()

def start_update():
    tl.start(block=False)
    

