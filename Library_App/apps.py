from django.apps import AppConfig


class LibraryAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'Library_App'
    
    ## For apschedular Configuration--------------
    def ready(self):
        from .scheduler import start_scheduler
        start_scheduler()
