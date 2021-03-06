# Generated by Django 3.2.12 on 2022-04-26 06:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('skarbonka', '0005_auto_20220412_0752'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='transaction',
            name='failed',
        ),
        migrations.AddField(
            model_name='transaction',
            name='status',
            field=models.PositiveSmallIntegerField(choices=[(1, 'Accepted'), (2, 'Pending'), (3, 'Failed'), (4, 'Declined')], default=1),
        ),
        migrations.AlterField(
            model_name='loan',
            name='status',
            field=models.PositiveSmallIntegerField(choices=[(1, 'Pending'), (2, 'Granted'), (3, 'Declined'), (4, 'Paid off'), (5, 'Expired')], default=1),
        ),
        migrations.AlterField(
            model_name='notification',
            name='resource',
            field=models.PositiveSmallIntegerField(choices=[(1, 'None'), (2, 'Transaction'), (3, 'Allowance'), (4, 'Loan'), (5, 'Withdraw')], default=1),
        ),
    ]
