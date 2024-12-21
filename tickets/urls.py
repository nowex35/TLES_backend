from django.urls import path
from . import views
from rest_framework.permissions import IsAdminUser
from rest_framework.decorators import api_view, permission_classes

urlpatterns = [
    # CSVファイルをデータベースにアップロードするエンドポイント
    path('upload/', views.CSVUploadView.as_view(), name='upload_csv'),

    # CSVファイルアップロード用のインターフェースページを表示するエンドポイント
    path('interface/', views.upload_csv_interface.as_view(), name='upload_csv_interface'),

    # データベースからフィルタリングしてチケットデータを取得するエンドポイント
    path('retrieve/', views.TicketViewSet.as_view({'get': 'list'}), name='retrieve_data'),

    # 加工済みのCSVファイルを返すエンドポイント
    path('process_csv/', views.upload_file, name='process_csv'),
]
