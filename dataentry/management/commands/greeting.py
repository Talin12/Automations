from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = 'Greets the user'

    def add_arguments(self, parser):
        parser.add_argument('name', type=str, help='Specify the name to greet')
    

    def handle(self, *args, **kwargs):
        name = kwargs['name']
        greeting = f'Hello {name}! Welcome to the Data Entry Application.'
        self.stdout.write(self.style.WARNING(greeting))