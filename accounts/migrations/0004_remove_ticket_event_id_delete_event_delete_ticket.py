# Generated by Django 5.0 on 2024-10-29 13:47

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0003_rename_special_viewing_ticket_special_viewing_freq_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='ticket',
            name='event_id',
        ),
        migrations.DeleteModel(
            name='Event',
        ),
        migrations.DeleteModel(
            name='Ticket',
        ),
    ]