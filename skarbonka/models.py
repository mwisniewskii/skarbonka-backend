from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone
from django_celery_beat.models import CrontabSchedule, PeriodicTask


class TransactionType(models.IntegerChoices):
    ORDINARY = 1, 'Ordinary'
    DEPOSIT = 2, 'Deposit'
    WITHDRAW = 3, 'Withdraw'
    LOAN = 4, 'Loan'
    ALLOWANCE = 5, 'Allowance'


class FrequencyType(models.IntegerChoices):
    DAILY = 1, 'Daily'
    WEEKLY = 2, 'Weekly'
    MONTHLY = 3, 'Monthly'


class Transaction(models.Model):
    """Models of user transactions."""

    sender = models.ForeignKey(
        'accounts.CustomUser', null=True, on_delete=models.SET_NULL, related_name='sender'
    )
    recipient = models.ForeignKey(
        'accounts.CustomUser', null=True, on_delete=models.SET_NULL, related_name='recipient'
    )
    datetime = models.DateTimeField(auto_now=True)
    title = models.CharField(max_length=255)
    description = models.CharField(max_length=255, null=True, blank=True)
    amount = models.DecimalField(max_digits=8, decimal_places=2)
    types = models.PositiveSmallIntegerField(
        choices=TransactionType.choices, default=TransactionType.ORDINARY
    )


class Allowance(models.Model):
    """Models of granted allowance."""

    parent = models.ForeignKey(
        'accounts.CustomUser',
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='parent',
    )
    child = models.ForeignKey(
        'accounts.CustomUser',
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='child',
    )
    created_at = models.DateTimeField(auto_now=True)
    amount = models.DecimalField(max_digits=8, decimal_places=2)
    frequency = models.PositiveSmallIntegerField(choices=FrequencyType.choices)
    execute_time = models.TimeField(null=True)
    day_of_month = models.IntegerField(
        default=1, validators=[MaxValueValidator(28), MinValueValidator(1)]
    )
    day_of_week = models.IntegerField(
        default=1, validators=[MaxValueValidator(7), MinValueValidator(1)]
    )
    task = models.OneToOneField(
        PeriodicTask,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )

    def delete(self, *args, **kwargs):
        if self.task is not None:
            self.task.delete()
        return super().delete(*args, **kwargs)

    def setup_task(self):
        self.task = PeriodicTask.objects.create(
            name=f'Allowance {self.pk} ',
            task='admit_allowance',
            crontab=self.interval,
            args=[self.parent.pk, self.child.pk, float(self.amount)],
            start_time=timezone.now(),
        )
        self.save()

    @property
    def interval(self):
        if self.frequency == FrequencyType.DAILY:
            crontab, _ = CrontabSchedule.objects.get_or_create(
                hour=self.execute_time.hour, minute=self.execute_time.minute, day_of_week='*'
            )
        elif self.frequency == FrequencyType.WEEKLY:
            crontab, _ = CrontabSchedule.objects.get_or_create(
                hour=self.execute_time.hour,
                minute=self.execute_time.minute,
                day_of_week=self.day_of_week,
            )
        elif self.frequency == FrequencyType.MONTHLY:
            crontab, _ = CrontabSchedule.objects.get_or_create(
                hour=self.execute_time.hour,
                minute=self.execute_time.minute,
                day_of_month=self.day_of_month,
            )
        return crontab
