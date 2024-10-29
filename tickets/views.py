from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Ticket
from .serializers import TicketSerializer
from rest_framework.permissions import AllowAny
import csv
import io
from datetime import datetime


# Create your views here.

class CSVUploadView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, format=None):
        # デバッグ用の出力
        print("リクエストの中身:", request.FILES)

        file = request.FILES.get('file')
        
        if not file:
            return Response({'error': 'ファイルが添付されていません'}, status=status.HTTP_400_BAD_REQUEST)
        
        if not file.name.endswith('.csv'):
            return Response({'error': 'CSVファイルをアップロードしてください'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            data = file.read().decode('utf-8')
            io_string = io.StringIO(data)
            reader = csv.DictReader(io_string)

            for row in reader:
                # purchase_datetimeの変換
                try:
                    purchase_datetime = datetime.strptime(row.get("購入日時"), "%Y/%m/%d %H:%M").isoformat()
                except ValueError:
                    return Response({'error': '購入日時の形式が不正です。YYYY/MM/DD HH:MM形式で入力してください。'}, status=status.HTTP_400_BAD_REQUEST)
                serializer = TicketSerializer(data={
                    'quantity': row.get("重複枚数"),
                    'Order_number': row.get("Order number"),
                    'purchase_datetime': purchase_datetime,
                    'ticket_type': row.get("チケット種類"),
                    'ticket_price': row.get("チケット価格"),
                    'seat_type': row.get("座席種"),
                    'coupon_applied': row.get("クーポン有無") != "クーポンなし",
                    'category': row.get("カテゴリー"),
                    'nationality': row.get("国籍") or "未指定",
                    'gender': row.get("性別"),
                    'age_group': row.get("年代"),
                    'school_year': row.get("学年"),
                    'department': row.get("所属"),
                    'referral_source': row.get("知ったきっかけ"),
                    'attendance_count': row.get("来場回数"),
                    'play_freq': row.get("スポーツ実施頻度"),
                    'viewing_freq': row.get("スポーツ観戦頻度"),
                    'special_viewing_freq': row.get("開催競技観戦頻度"),
                    'event_id': row.get("event_id"),
                })
                if serializer.is_valid():
                    serializer.save()
                else:
                    print("シリアライザのエラー:", serializer.errors)
                    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                
            return Response({"message": "データが正常にインポートされました"}, status=status.HTTP_201_CREATED)
        
        except Exception as e:
            print("例外エラー:", str(e))
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)




from django.shortcuts import render
def upload_csv_interface(request):
    return render(request, 'tickets/upload_csv.html')