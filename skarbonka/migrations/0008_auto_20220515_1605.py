# Generated by Django 3.2.12 on 2022-05-15 14:05

import django.core.validators
from django.db import migrations, models
import django_fsm


class Migration(migrations.Migration):

    dependencies = [
        ('skarbonka', '0007_transaction_state'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='notification',
            name='resource',
        ),
        migrations.RemoveField(
            model_name='notification',
            name='target',
        ),
        migrations.AddField(
            model_name='notification',
            name='url',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='amount',
            field=models.DecimalField(decimal_places=2, max_digits=8, validators=[django.core.validators.MinValueValidator(0.01)]),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='state',
            field=django_fsm.FSMField(choices=[('accepted', 'Accepted'), ('pending', 'Pending'), ('failed', 'Failed'), ('declined', 'Declined'), ('to confirm', 'Require Confirmation')], default='pending', max_length=50),
        ),
    ]
