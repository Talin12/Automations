from django.urls import path
from . import views

urlpatterns = [
    path('importdata/', views.import_data, name='import_data'),
]