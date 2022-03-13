# Generated by Django 3.2.12 on 2022-03-13 23:16

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Family',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
            ],
        ),
        migrations.AddField(
            model_name='customuser',
            name='balance',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=8),
        ),
        migrations.AddField(
            model_name='customuser',
            name='parental_control',
            field=models.PositiveSmallIntegerField(choices=[(1, 'None'), (2, 'Confirmation'), (3, 'Periodic limit')], default=1),
        ),
        migrations.AddField(
            model_name='customuser',
            name='user_type',
            field=models.PositiveSmallIntegerField(choices=[(1, 'Parent'), (2, 'Child')], default=1),
        ),
        migrations.AddField(
            model_name='customuser',
            name='family',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='accounts.family'),
        ),
    ]
