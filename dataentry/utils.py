import csv
import hashlib
import time
from django.apps import apps
from django.core.management import CommandError
from django.db import DataError
from django.core.mail import EmailMessage
from django.conf import settings
from emails.models import Email, Sent, EmailTracking, Subscriber
from bs4 import BeautifulSoup
import datetime
import os

def get_all_custom_models():
    default_models = ['ContentType', 'Session', 'Permission', 'Group', 'LogEntry', 'Upload', 'User']

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

def send_email_notification(mail_subject, message, to_email, attachment=None, email_id=None):
    try:
        from_email = settings.DEFAULT_FROM_EMAIL
        for recipient_email in to_email:
            # Creating Email Tracking Record
            new_message = message
            if email_id:
                email = Email.objects.get(pk=email_id)
                subscriber = Subscriber.objects.get(email_list=email.email_list, email_address=recipient_email)
                timestamp = str(time.time())
                data_to_hash = f"{recipient_email}{timestamp}"
                unique_id = hashlib.sha256(data_to_hash.encode()).hexdigest()
                email_tracking = EmailTracking.objects.create(
                    email=email,
                    subscriber=subscriber,
                    unique_id=unique_id
                )
                # Generate the tracking pixel
                base_url = settings.BASE_URL
                click_tracking_url = f"{base_url}/emails/track/click/{unique_id}/"
                open_tracking_url = f"{base_url}/emails/track/open/{unique_id}/"

                # Search for the links in the Email body 
                soup = BeautifulSoup(message, 'html.parser')
                urls = [a['href'] for a in soup.find_all('a', href=True)]

                # If there are links or urls in the body inject our tracking url to that original link
                if urls:
                    for url in urls:
                        # Create a tracked URL
                        tracking_url = f"{click_tracking_url}?url={url}"
                        # Replace the original URL with the tracked URL in the email body
                        new_message = new_message.replace(f"{url}",f"{tracking_url}")
                else:
                    print("No Url's Found in the Email Body")
                # Injecting the open tracking pixel
                open_tracking_img = f"<img src='{open_tracking_url}' width='1' height='1'/>"
                new_message += open_tracking_img

            print(f"new_message: {new_message}")
            mail = EmailMessage(mail_subject, new_message, from_email, to=[recipient_email])

            if attachment is not None:
                mail.attach_file(attachment)

            mail.content_subtype = "html"
            mail.send()

        # Storing the sent email info into the models
        if email_id:
            sent = Sent()
            sent.email = email
            sent.total_sent = email.email_list.count_emails()
            sent.save()
    except Exception as e:
        raise e
    
def generate_csv_path(model_name):
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

    export_dir = 'exported_data'

    file_name = f'exported_{model_name}_data_{timestamp}.csv'
    file_path = os.path.join(settings.MEDIA_ROOT, export_dir, file_name)

    return file_path