def get_notifications():
    from django.apps import apps
    from .models import Notification

    app_config = apps.get_app_config("notify")

    out = []

    for model in app_config.get_models():
        if issubclass(model, Notification):
            objs = list(model.objects.filter(enable=True))
            out += objs

    return out
