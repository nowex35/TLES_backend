from django.contrib.auth import get_user_model
from rest_framework.generics import RetrieveAPIView
from rest_framework.permissions import AllowAny


from .serializers import UserSerializer

User = get_user_model()

# ユーザー詳細
class UserDetailView(RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    # 認証なしでアクセス可能
    permission_classes = (AllowAny,)
    # URLから取得するパラメータ名を指定
    lookup_field = "uid"