from django.urls import path, include
from . import views
urlpatterns = [
    path('upload/', views.CSVUploadView.as_view(), name='upload_csv'),
    path('interface/', views.upload_csv_interface.as_view(), name='upload_csv_interface'),
    path('retrieve/', views.TicketViewSet.as_view({'get':'list'}), name='retrieve_data'),
]