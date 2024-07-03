from key_images_app.auth.middleware.authmiddleware import get_request_tenant_id
from key_images_app.tenants.tenantservice import get_tenant_db

class DbRouter:

    def db_for_read(self, model, **hints):
        db_name = self.get_current_db_name()
        return db_name

    def db_for_write(self, model, **hints):
        db_name = self.get_current_db_name()
        return db_name

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        return True

    def get_current_db_name(self):
        tenant_id = get_request_tenant_id()
        db_name = None
        if tenant_id:
            db_name = get_tenant_db(tenant_id)        
        return db_name