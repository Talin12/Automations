from awd_main.celery import app
from django.core.management import call_command
from django.core.mail import EmailMessage
from django.conf import settings
from .utils import send_email_notification
import time

@app.task
def celery_test_task():
    time.sleep(10)

    mail_subject = 'Data Import Completed'
    message = 'Your data import task has been completed successfully.'
    to_email = settings.DEFAULT_TO_EMAIL

    send_email_notification(mail_subject, message, to_email)
    return "Email Sent Successfully!!"

@app.task
def import_data_task(file_path, model_name):
    try:
        call_command('importdata', file_path, model_name)
    except Exception as e:
        raise e
    
    # We want to Send an Email here 

    mail_subject = 'Importing Data Completed'
    message = 'Your data import task has been completed successfully.'
    to_email = settings.DEFAULT_TO_EMAIL
    send_email_notification(mail_subject, message, to_email)

    
    return "Data Imported Successfully!!"