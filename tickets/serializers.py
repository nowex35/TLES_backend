from rest_framework import serializers
from .models import Ticket

class TicketSerializer(serializers.ModelSerializer):
    # データとJSONの相互変換を行える
    class Meta:
        model = Ticket
        fields = "__all__"