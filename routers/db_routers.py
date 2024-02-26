class UserRouter:
    '''
    The user router has been registered in the settings.py
    DATABASE_ROUTERS Array. It will reroute
    all the queries done via the route_app_labels
    to the postgres database "return 'postgres'"
    '''
    route_app_labels = {'auth', 'authentication', 'authtoken', 'contenttypes',
                        'sessions', 'token_blacklist',}

    def db_for_read(self, model, **hints):
        if model._meta.app_label in self.route_app_labels:
            return 'postgres'
        return None

    def db_for_write(self, model, **hints):
        if model._meta.app_label in self.route_app_labels:
            return 'postgres'
        return None

    def allow_relation(self, obj1, obj2, **hints):
        if (
            obj1._meta.app_label in self.route_app_labels or
            obj2._meta.app_label in self.route_app_labels
        ):
            return True
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        if app_label in self.route_app_labels:
            return db == 'postgres'
        return None

class PredictionsRouter:
    '''
    The predictions router has been registered in the settings.py
    DATABASE_ROUTERS Array. It will reroute
    all the queries for the survey to the postgres DB
    '''
    route_app_labels= {'anomaly_detection',}
    def db_for_read(self, model, **hints):
        if model._meta.app_label in self.route_app_labels:
            return 'postgres'
        return None

    def db_for_write(self, model, **hints):
        if model._meta.app_label in self.route_app_labels:
            return 'postgres'
        return None

    def allow_relation(self, obj1, obj2, **hints):
        if (
            obj1._meta.app_label in self.route_app_labels or
            obj2._meta.app_label in self.route_app_labels
        ):
            return True
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        if app_label in self.route_app_labels:
            return db == 'postgres'
        return None