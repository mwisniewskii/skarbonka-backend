# Generated by Django 3.2.12 on 2022-04-26 06:52

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0003_remove_customuser_balance'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='days_limit_period',
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='customuser',
            name='sum_periodic_limit',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=8, null=True),
        ),
        migrations.AlterField(
            model_name='customuser',
            name='family',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='family', to='accounts.family'),
        ),
    ]
