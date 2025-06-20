# Generated by Django 4.2.22 on 2025-06-11 05:21

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
        ('caterers', '0002_caterer_is_active_caterer_is_suspended_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='caterer',
            name='provider',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='caterers', to='accounts.providerprofile'),
        ),
    ]
