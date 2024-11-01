from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("api/auth/", include("djoser.urls")),
    path("api/auth/", include("djoser.urls.jwt")),
    #アカウント
    path("api/", include("accounts.urls")),
    path('admin/', admin.site.urls),
    #チケット
    path("api/tickets/", include("tickets.urls")),  # ここでticketsアプリのURLをインクルード
]
