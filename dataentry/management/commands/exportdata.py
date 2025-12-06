from django.core.management.base import BaseCommand
import csv
from django.apps import apps
from dataentry.utils import generate_csv_path
import datetime

# Proposed Command = python manage.py exportdata model_name
class Command(BaseCommand):
    help = 'Export data from the database to a CSV file.'

    def add_arguments(self, parser):
        parser.add_argument('model_name', type=str, help='The name of the model to export data from.')
        pass

    def handle(self, *args, **kwargs):
        model_name = kwargs['model_name'].capitalize()

        # Search for the model in all installed apps

        model = None
        for app_config in apps.get_app_configs():
            try:
                model = apps.get_model(app_config.label ,model_name)
                break
            except LookupError:
                pass

        if not model:
            self.stderr.write(f'Model "{model_name}" not found in any installed app.\n')
            return
        

        #fetch the data entries
        data = model.objects.all()

        # Define the CSV file path
        file_path = generate_csv_path(model_name)

        # Open the CSV file for writing
        with open(file_path, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)

            # Write the header row
            writer.writerow([field.name for field in model._meta.fields])

            # Write data rows
            for dt in data:
                writer.writerow([getattr(dt, field.name) for field in model._meta.fields])

        self.stdout.write(self.style.SUCCESS(f'Data successfully exported to {file_path}'))