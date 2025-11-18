from django.core.management.base import BaseCommand, CommandError
from django.apps import apps
import csv

# Proposed command: python manage.py importdata file_path

class Command(BaseCommand):
    help = 'It will import data from a specified file to the database'

    def add_arguments(self, parser):
        parser.add_argument('file_path', type=str, help='Path to the CSV file')
        parser.add_argument('model_name', type=str, help='Name of the model')

    def handle(self, *args, **kwargs):

        file_path = kwargs['file_path']
        model_name = kwargs['model_name'].capitalize()

        print(f'Importing data from file: {file_path}')
        print(f'Target model: {model_name}')

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
            #self.stdout.write(self.style.ERROR(f'Model {model_name} not found in any app.'))

        with open(file_path, 'r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                model.objects.create(**row)

        self.stdout.write(self.style.SUCCESS('Data imported Successfully!'))