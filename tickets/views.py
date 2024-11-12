from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.shortcuts import render
from django.views import View
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import viewsets,status
from .models import Ticket
from .serializers import TicketSerializer
from rest_framework.permissions import AllowAny
from django.views.decorators.csrf import csrf_exempt
from django.utils.translation import gettext as _
from django.core.files.storage import FileSystemStorage
from django.core.exceptions import ValidationError
from .preprocessing import allpreprocessing, allpreprocessing_full, allpreprocessing_customer
import mimetypes
import chardet
import logger
import zipfile
from django.http import HttpResponse
import pandas as pd
import csv
from django.conf import settings
import os
import io
from datetime import datetime
from django.db.models import Q

# CSVファイルのアップロードとデータ保存を行うビュー
class CSVUploadView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, format=None):
        file = request.FILES.get('file')
        
        # ファイルが添付されているかを確認
        if not file:
            return Response({'error': 'ファイルが添付されていません'}, status=status.HTTP_400_BAD_REQUEST)
        
        # ファイルの拡張子がCSVであるか確認
        if not file.name.endswith('.csv'):
            return Response({'error': 'CSVファイルをアップロードしてください'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            data = file.read().decode('utf-8')
            io_string = io.StringIO(data)
            reader = csv.DictReader(io_string)

            for row in reader:
                try:
                    # 購入日時の変換
                    purchase_datetime = datetime.strptime(row.get("購入日時"), "%Y/%m/%d %H:%M").isoformat()
                    
                    # シリアライザでデータのバリデーションと保存
                    serializer = TicketSerializer(data={
                        'quantity': row.get("重複枚数") or 0,
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
                        'grade': row.get("学年"),
                        'department': row.get("所属") or "無回答",
                        'referral_source': row.get("知ったきっかけ"),
                        'attendance_count': row.get("来場回数") or "無回答",
                        'play_freq': row.get("スポーツ実施頻度"),
                        'viewing_freq': row.get("スポーツ観戦頻度"),
                        'special_viewing_freq': row.get("開催競技観戦頻度") or "無回答",
                        'event_id': row.get("event_id"),
                    })
                    
                    # バリデーションエラーチェック
                    if serializer.is_valid():
                        serializer.save()
                    else:
                        print("シリアライザのエラー:", serializer.errors)
                        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                
                except ValueError:
                    return Response({'error': '購入日時の形式が不正です。YYYY/MM/DD HH:MM形式で入力してください。'}, status=status.HTTP_400_BAD_REQUEST)
            
            return Response({"message": "データが正常にインポートされました"}, status=status.HTTP_201_CREATED)
        
        except Exception as e:
            print("例外エラー:", str(e))
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


# HTMLテンプレートの表示を行うビュー
class upload_csv_interface(View):
    template_name = 'tickets/upload_csv.html'
    
    def get(self, request):
        return render(request, self.template_name)


# 動的なフィルタリングと特定カラムの取得を行うビュー
class TicketViewSet(viewsets.ModelViewSet):
    permission_classes = [AllowAny]
    queryset = Ticket.objects.all()
    serializer_class = TicketSerializer
    
    @method_decorator(cache_page(60 * 15))  # キャッシュを15分に設定
    def list(self, request, *args, **kwargs):
        """
            チケット情報を取得するAPI

            Parameters:
                quantity (list): 数量
                purchase_date (list): 購入日
                ticket_type (list): チケットタイプ
                ... 他のパラメータ

            Returns:
                Response: チケット情報のリスト
            """
        try:
            # クエリパラメータを利用したフィルタ条件の取得
            quantity = request.query_params.getlist('quantity')
            purchase_datetime = request.query_params.getlist('purchase_datetime')
            ticket_type = request.query_params.getlist('ticket_type')
            ticket_price = request.query_params.getlist('ticket_price')
            seat_type = request.query_params.getlist('seat_type')
            coupon_applied = request.query_params.getlist('coupon_appiled')
            category = request.query_params.getlist('category')
            nationality = request.query_params.getlist('nationality')
            gender = request.query_params.getlist('gender')
            age_group = request.query_params.getlist('age_group')
            grade = request.query_params.getlist('grade')
            department = request.query_params.getlist('department')
            attendance_count = request.query_params.getlist('attendance_count')
            play_freq = request.query_params.getlist('play_freq')
            viewing_freq = request.query_params.getlist('viewing_freq')
            special_viewing_freq = request.query_params.getlist('special_viewing_freq')
            event_id = request.query_params.getlist('event_id')
            purchase_dates = request.query_params.getlist('purchase_date')  # 複数の日付を取得
            purchase_times = request.query_params.getlist('purchase_time')  # 複数の時間を取得
            fields = request.query_params.get('fields')  # 取得カラム（例: "category,ticket_type"）

            # フィルタ条件に基づいてクエリセットを生成
            query = Q()
            if event_id:
                query &= Q(event_id__in=event_id)
            if quantity:
                query &= Q(quantity__in=quantity)
            if purchase_datetime:
                query &= Q(purchase_datetime__in=purchase_datetime)
            if ticket_type:
                query &= Q(ticket_type__in=ticket_type)
            if ticket_price:
                query &= Q(ticket_price__in=ticket_price)
            if seat_type:
                query &= Q(seat_type__in=seat_type)
            if coupon_applied:
                query &= Q(coupon_applied__in=coupon_applied)
            if category:
                query &= Q(category__in=category)
            if nationality:
                query &= Q(nationality__in=nationality)
            if gender:
                query &= Q(gender__in=gender)
            if age_group:
                query &= Q(age_group__in=age_group)
            if grade:
                query &= Q(grade__in=grade)
            if department:
                query &= Q(department__in=department)
            if attendance_count:
                query &= Q(attendance_count__in=attendance_count)
            if play_freq:
                query &= Q(play_freq__in=play_freq)
            if viewing_freq:
                query &= Q(viewing_freq__in=viewing_freq)
            if special_viewing_freq:
                query &= Q(special_viewing_freq__in=special_viewing_freq)
            if purchase_dates:
                query &= Q(purchase_datetime__date__in=purchase_dates)  # 日付部分でフィルタリング
            if purchase_times:
                query &= Q(purchase_datetime__time__in=purchase_times)  # 時間部分でフィルタリング

            # クエリに基づいてチケットデータを取得
            queryset = self.get_queryset().filter(query)

            # 特定のカラムのみを返すか全カラムを返すかの処理
            if fields:
                fields_list = fields.split(",")  # カンマ区切りでカラム指定をリスト化
                serializer = self.get_serializer(queryset, many=True, fields=fields_list)
            else:
                serializer = self.get_serializer(queryset, many=True)  # 全カラムを返す

            # シリアライズしたデータをレスポンスとして返す
            return Response(serializer.data)

        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


# アップロードされたファイルを一時保存するためのパス
UPLOAD_DIR = os.path.join(settings.BASE_DIR, 'ProcessData_tl_uploaded_files')
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

fs = FileSystemStorage(location=UPLOAD_DIR)

@csrf_exempt  # CSRF対策を適用するため、フロントエンドでトークンを使用することを推奨
def upload_file(request):
    if request.method == 'POST' and request.FILES.get('csv_file'):
        csv_file = request.FILES['csv_file']
        event_id = request.POST.get('event_id')
        
        try:
            # ファイルのMIMEタイプを確認
            mime_type, _ = mimetypes.guess_type(csv_file.name)
            if mime_type not in ['application/vnd.ms-excel', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', 'text/csv']:
                raise ValidationError(_('無効なファイル形式です。CSVまたはExcelファイルをアップロードしてください。'))

            # ファイルを一時保存
            saved_file_path = fs.save(csv_file.name, csv_file)
            saved_file_full_path = os.path.join(UPLOAD_DIR, saved_file_path)

            # ファイルをDataFrameとして読み込む
            file_name = csv_file.name.lower()
            if file_name.endswith('.xlsx') or file_name.endswith('.xls'):
                # Excelファイルとして読み込む
                df = pd.read_excel(saved_file_full_path, engine='openpyxl')
            else:
                # CSVファイルとして読み込むためにエンコーディングを推測
                with open(saved_file_full_path, 'rb') as f:
                    raw_data = f.read()
                    result = chardet.detect(raw_data)
                    encoding = result['encoding']
                df = pd.read_csv(saved_file_full_path, encoding=encoding)

            # ファイル内容の基本検証
            if df.empty:
                raise ValidationError(_('アップロードされたファイルは空です。適切なデータを含むファイルをアップロードしてください。'))
            if len(df.columns) < 1:
                raise ValidationError(_('アップロードされたファイルに有効な列がありません。適切なデータを含むファイルをアップロードしてください。'))

            # 前処理関数が定義されているか確認
            if allpreprocessing is None:
                logger.error("allpreprocessing function is not defined")
                raise ValueError("allpreprocessing function is not defined")

            # 前処理を実行
            processed_df = allpreprocessing(df)
            processed_full_df = allpreprocessing_full(df.copy())
            processed_customer_df = allpreprocessing_customer(df.copy())

            # 元のファイル名（拡張子なし）を取得してZIPファイルの名前に使用
            file_name_base = os.path.splitext(csv_file.name)[0]

            # メモリ上でZIPファイルを作成
            zip_buffer = io.BytesIO()
            with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zf:
                # ExcelファイルとShift_JISエンコーディングのCSVファイルをZIPに追加
                for df, label in [(processed_df, 'cut'), (processed_full_df, 'full'), (processed_customer_df, 'customer_info')]:
                    excel_buffer = io.BytesIO()
                    with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
                        df.to_excel(writer, index=False, sheet_name='Sheet1')
                    excel_buffer.seek(0)
                    zf.writestr(f'{file_name_base}_{label}.xlsx', excel_buffer.getvalue())

                    # Shift_JISエンコーディングのCSVも追加
                    sjis_csv_buffer = io.StringIO()
                    df.to_csv(sjis_csv_buffer, index=False, encoding='shift_jis')
                    sjis_csv_buffer.seek(0)
                    zf.writestr(f'{file_name_base}_{label}.csv', sjis_csv_buffer.getvalue())

            # ZIPファイルをHTTPレスポンスとして返す
            zip_buffer.seek(0)
            response = HttpResponse(zip_buffer, content_type='application/zip')
            response['Content-Disposition'] = f'attachment; filename={file_name_base}.zip'

            return response

        except ValidationError as ve:
            logger.error("Validation error: %s" % str(ve))
            return HttpResponse(str(ve), status=400)
        except ValueError as ve:
            logger.error("Value error: %s" % str(ve))
            return HttpResponse(str(ve), status=500)
        except Exception as e:
            logger.error("Error processing file: %s" % str(e))
            return HttpResponse("エラーが発生しました。後でもう一度お試しください。", status=500)

        finally:
            # 一時ファイルのクリーンアップ
            if os.path.exists(saved_file_full_path):
                try:
                    os.remove(saved_file_full_path)
                except Exception as e:
                    logger.error("Failed to delete %s. Reason: %s" % (saved_file_full_path, str(e)))

    return render(request, 'preprocessing/upload.html')

# 一時ファイルのクリーンアップ
def cleanup_temp_files():
    for filename in os.listdir(UPLOAD_DIR):
        file_path = os.path.join(UPLOAD_DIR, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
        except Exception as e:
            logger.error(f'Failed to delete {file_path}. Reason: {e}')