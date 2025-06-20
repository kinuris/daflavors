# Generated by Django 4.2.22 on 2025-06-09 00:01

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('venues', '0002_remove_venue_feature_and_room_models'),
    ]

    operations = [
        migrations.AddField(
            model_name='venue',
            name='is_active',
            field=models.BooleanField(default=True, help_text='Whether this venue is active and accepting bookings'),
        ),
        migrations.AddField(
            model_name='venue',
            name='is_suspended',
            field=models.BooleanField(default=False, help_text='Whether this venue has been suspended by admin'),
        ),
        migrations.AddField(
            model_name='venue',
            name='suspended_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='venue',
            name='suspended_by',
            field=models.ForeignKey(blank=True, limit_choices_to={'is_staff': True}, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='suspended_venues', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='venue',
            name='suspension_reason',
            field=models.TextField(blank=True, help_text='Reason for suspension (admin only)'),
        ),
    ]
