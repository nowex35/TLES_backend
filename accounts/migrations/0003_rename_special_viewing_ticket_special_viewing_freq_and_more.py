# Generated by Django 5.0 on 2024-10-29 11:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_event_ticket'),
    ]

    operations = [
        migrations.RenameField(
            model_name='ticket',
            old_name='special_viewing',
            new_name='special_viewing_freq',
        ),
        migrations.AddField(
            model_name='ticket',
            name='order_number',
            field=models.CharField(default='', max_length=50, verbose_name='購入識別番号'),
        ),
        migrations.AddField(
            model_name='ticket',
            name='ticket_count',
            field=models.PositiveIntegerField(default=0, verbose_name='重複枚数'),
        ),
    ]