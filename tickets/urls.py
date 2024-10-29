from django.urls import path
from . import views

urlpatterns = [
    path('upload/', views.CSVUploadView.as_view(), name='upload_csv'),
    path('interface/', views.upload_csv_interface, name='upload_csv_interface'),
]