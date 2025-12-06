from django.shortcuts import render, redirect
from .utils import check_csv_errors, get_all_custom_models
from uploads.models import Upload
from django.conf import settings
from django.contrib import messages
from .tasks import import_data_task, export_data_task
from django.core.management import call_command

# Create your views here.

def import_data(request):
    context = {}
    if request.method == 'POST':
        file_path = request.FILES.get('file_path')
        model_name = request.POST.get('model_name')

        #Storing the file inside the upload model
        upload = Upload.objects.create(file=file_path, model_name=model_name)

        #Construct the full file path
        relative_path = str(upload.file.url)
        base_url = str(settings.BASE_DIR)

        file_path = base_url + relative_path

        #Checking for the CSV's Error
        try:
            check_csv_errors(file_path, model_name)
        except Exception as e:
            messages.error(request, f'Error in CSV File: {str(e)}')
            return redirect('import_data')

        # Handle the import data task here
        import_data_task.delay(file_path, model_name)        

        # Show the message to the user
        messages.success(request, 'Your data is being imported in the background. You will be notified on completion.')
        return redirect('import_data')
    else:
        custom_models = get_all_custom_models()
        context = {
            'custom_models': custom_models,
        }
    return render(request, 'dataentry/importdata.html', context)

def export_data(request):
    if request.method == 'POST':
        model_name = request.POST.get('model_name')
        # Logic to export data for the selected model
        export_data_task.delay(model_name)
        messages.success(request, 'Your data export is being processed in the background. You will be notified on completion.')
        return redirect('export_data')
    else:
        custom_models = get_all_custom_models()
        context = {
            'custom_models': custom_models,
        }
    return render(request, 'dataentry/exportdata.html', context)