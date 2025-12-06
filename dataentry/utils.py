from django.apps import apps
import csv
from django.core.management import CommandError
from django.db import DataError
from django.core.mail import EmailMessage
from django.conf import settings

def get_all_custom_models():
    default_models = ['ContentType', 'Session', 'Permission', 'Group', 'LogEntry', 'Upload']

    custom_models = []
    
    for model in apps.get_models():
        if model.__name__ not in default_models:
            custom_models.append(model.__name__)
    return custom_models

def check_csv_errors(file_path, model_name):
    model = None
    for app_config in apps.get_app_configs():
        #We will try to search for the Model
        try:
            model = apps.get_model(app_config.label, model_name)
            break
        except LookupError:
            continue # this means model not found in the cuurent app, switching to next one 

    if not model:
        raise CommandError(f'Model {model_name} not found in any app!')
    
    #Compare csv Heafer with model field names
    model_fields = [field.name for field in model._meta.fields if field.name != 'id']

    try:
        with open(file_path, 'r') as file:
            reader = csv.DictReader(file)
            csv_header = reader.fieldnames

        # Validate CSV Header
            if set(csv_header) != set(model_fields):
                raise DataError('CSV header does not match model fields!')
    except Exception as e:
        raise e
    
    return model

def send_email_notification(mail_subject, message, to_email):

    try:
        from_email = settings.DEFAULT_FROM_EMAIL
        mail = EmailMessage(mail_subject, message, from_email, to=[to_email])
        mail.send()
    except Exception as e:
        raise e