import base64

from rest_framework import serializers
from django.core.files.base import ContentFile

#Base64エンコードされた画像データを受け取るカスタムフィールド
class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        #Base64エンコードされた画像データを受け取る
        if isinstance(data, str) and data.startswith("data:image"):
            #Base64データを取り出す
            format, imgstr = data.split(";base64,")
            #画像データをデコード
            ext = format.split("/")[-1]
            # Base64エンコードされた画像データをでコードし、ContentFileオブジェクトを作成
            data = ContentFile(base64.b64decode(imgstr), name="temp." + ext)
        return super(Base64ImageField, self).to_internal_value(data)