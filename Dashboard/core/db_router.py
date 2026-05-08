class BotDBRouter:
    def db_for_read(self, model, **hints):
        if hasattr(model, 'use_bot_db') and model.use_bot_db:
            return 'bot'
        return None

    def db_for_write(self, model, **hints):
        if hasattr(model, 'use_bot_db') and model.use_bot_db:
            return 'bot'
        return None

    def allow_relation(self, obj1, obj2, **hints):
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        from django.apps import apps
        try:
            model = apps.get_model(app_label, model_name)
            if hasattr(model, 'use_bot_db') and model.use_bot_db:
                return False
        except LookupError:
            pass
        return None
