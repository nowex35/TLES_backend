from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth import get_user_model
from .models import Event, Ticket  # EventとTicketモデルをインポート

User = get_user_model()

class UserAdminCustom(UserAdmin):
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "uid",
                    "name",
                    "email",
                    "password",
                    "avatar",
                    "introduction",
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "updated_at",
                    "created_at",
                ),
            },
        ),
    )
    
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "name",
                    "email",
                    "password1",
                    "password2",
                    "is_active",
                    "is_staff",
                    "is_superuser",
                ),
            },
        ),
    )

    list_display = (
        "uid",
        "name",
        "email",
        "is_active",
        "updated_at",
        "created_at",
    )
    
    list_filter = ()
    search_fields = (
        "uid",
        "email",
    )
    ordering = ("updated_at",)
    list_display_links = ("uid", "name", "email")
    readonly_fields = ("updated_at", "created_at", "uid")
    
admin.site.register(User, UserAdminCustom)


# Eventモデル用の管理クラス
class EventAdmin(admin.ModelAdmin):
    list_display = ("event_id", "sport_name", "game_date", "release_date", "opponent_team", "place")
    search_fields = ("sport_name", "opponent_team", "place")
    list_filter = ("sport_name", "game_date")
    ordering = ("-game_date",)
    readonly_fields = ("event_id",)

admin.site.register(Event, EventAdmin)

from django.contrib import messages
from django.utils.translation import ngettext
# Ticketモデル用の管理クラス
class TicketAdmin(admin.ModelAdmin):
    list_display = (
        "ticket_id",
        "order_number",
        "quantity",
        "purchase_datetime",
        "ticket_type",
        "ticket_price",
        "seat_type",
        "category",
        "gender",
        "age_group",
        "grade",
        "department",
        "event_id",
    )
    search_fields = ("order_number", "ticket_type", "category", "gender", "age_group", "department")
    list_filter = ("ticket_type", "category", "gender", "age_group", "grade", "department", "event_id")
    ordering = ("-purchase_datetime",)
    readonly_fields = ("ticket_id",)
    
    def delete_tickets_by_event(self, request, queryset):
        # event_idを指定して削除
        event_id = request.POST.get('event_id')  # フォームから event_id を取得
        if event_id:
            tickets_deleted, _ = queryset.filter(event_id=event_id).delete()
            self.message_user(request, ngettext(
                '%d Ticket was successfully deleted.',
                '%d Tickets were successfully deleted.',
                tickets_deleted,
            ) % tickets_deleted, messages.SUCCESS)
        else:
            self.message_user(request, "Event IDが指定されていません。", messages.WARNING)
    
    delete_tickets_by_event.short_description = "特定のEvent IDのチケットを一括削除"

admin.site.register(Ticket, TicketAdmin)
