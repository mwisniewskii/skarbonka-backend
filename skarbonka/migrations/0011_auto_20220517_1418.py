# Generated by Django 3.2.12 on 2022-05-17 12:18

from decimal import Decimal
import django.core.validators
from django.db import migrations, models
import django_fsm


class Migration(migrations.Migration):

    dependencies = [
        ('skarbonka', '0010_remove_transaction_status'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='loan',
            name='status',
        ),
        migrations.AddField(
            model_name='loan',
            name='state',
            field=django_fsm.FSMField(choices=[(1, 'Pending'), (2, 'Granted'), (3, 'Declined'), (4, 'Paid off'), (5, 'Expired')], default=1, max_length=50),
        ),
        migrations.AlterField(
            model_name='allowance',
            name='amount',
            field=models.DecimalField(decimal_places=2, max_digits=8, validators=[django.core.validators.MinValueValidator(Decimal('0.01'))]),
        ),
        migrations.AlterField(
            model_name='loan',
            name='amount',
            field=models.DecimalField(decimal_places=2, max_digits=8, validators=[django.core.validators.MinValueValidator(Decimal('0.01'))]),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='amount',
            field=models.DecimalField(decimal_places=2, max_digits=8, validators=[django.core.validators.MinValueValidator(Decimal('0.01'))]),
        ),
    ]
