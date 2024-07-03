import logging
import psycopg


from django.core.management.commands.migrate import Command as MigrationCommand
from django.core.management.base import BaseCommand, CommandError
from django.db import connections
from django.conf import settings
from django.core.management import call_command

from Annotations_app.tenants.dbsettings import *


class Command(BaseCommand):

    def handle(self, *args, **options):
        # update list of db resources from tenant manager
        update_db_configs()

        # update table models
        call_command("makemigrations")

        # create tables and schemas
        for db_key in connections.databases:
            msg = 'Migrating database: {dbname}'.format( dbname=db_key)            
            logging.info(msg)
            if db_key != 'default':
                self.create_schema(db_key)
            call_command("migrate", database=db_key, interactive=False, skip_checks=False)
        

    # tries to create the schema if it doesn't exists
    def create_schema(self, db_key):
        config = connections.databases[db_key]
        if config:
            conn = psycopg.connect(
                host = config['HOST'], 
                port = config['PORT'], 
                dbname = config['NAME'], 
                user = config['USER'], 
                password = config['PASSWORD'] 
            )
            user = config['USER']
            try:
                with conn.cursor() as cursor:
                    cursor.execute( f"CREATE SCHEMA IF NOT EXISTS {db_key}" )
                    cursor.execute( f"GRANT ALL ON schema {db_key} TO {user}" )
                    conn.commit()
            except Exception as e:
                logging.error(f'Exception {str(e)}')

            conn.close()

