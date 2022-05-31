# Standard Library
import datetime
from decimal import Decimal

# Django
from django.core.validators import MaxValueValidator
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import Sum
from django.utils import timezone

# 3rd-party
from django_celery_beat.models import ClockedSchedule
from django_celery_beat.models import CrontabSchedule
from django_celery_beat.models import PeriodicTask
from django_fsm import FSMField
from django_fsm import FSMIntegerField
from django_fsm import can_proceed
from django_fsm import transition

# Local
from .enum import FrequencyType
from .enum import LoanState
from .enum import TransactionState
from .enum import TransactionType
from .state_conditions import confirmation_control
from .state_conditions import is_paid
from .state_conditions import loan_funds_enough
from .state_conditions import period_limit_check
from .state_conditions import sender_funds_enough


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
    amount = models.DecimalField(
        max_digits=8, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))]
    )
    types = models.PositiveSmallIntegerField(
        choices=TransactionType.choices, default=TransactionType.ORDINARY
    )
    loan = models.ForeignKey('skarbonka.Loan', null=True, blank=True, on_delete=models.SET_NULL)
    state = FSMIntegerField(choices=TransactionState.choices, default=TransactionState.PENDING)

    @transition(
        field=state,
        source=TransactionState.PENDING,
        target=TransactionState.ACCEPTED,
        conditions=[sender_funds_enough, period_limit_check],
        on_error=TransactionState.FAILED,
    )
    def accept(self):
        pass

    @transition(
        field=state,
        source=TransactionState.PENDING,
        target=TransactionState.TO_CONFIRM,
        conditions=[confirmation_control],
    )
    def to_confirm(self):
        notifications = []
        for parent in self.sender.family.parents:
            notifications.append(
                Notification(
                    recipient=parent,
                    content=f"{self.sender} chcę dokonać transakcji na kwotę {self.amount}.",
                )
            )
        Notification.objects.bulk_create(notifications)

    @transition(field=state, source=TransactionState.TO_CONFIRM, target=TransactionState.DECLINED)
    def decline(self, parent):
        Notification.objects.create(
            recipient=self.sender,
            content=f"Transakcja na kwotę {self.amount} została odrzucona przez {parent}.",
        )

    @transition(
        field=state,
        source=TransactionState.TO_CONFIRM,
        target=TransactionState.ACCEPTED,
        conditions=[sender_funds_enough],
        on_error=TransactionState.FAILED,
    )
    def parent_accept(self, parent):
        Notification.objects.create(
            recipient=self.sender,
            content=f"Transakcja na kwotę {self.amount} została zaakceptowana przez {parent}.",
        )

    @transition(
        field=state,
        source='*',
        target=TransactionState.FAILED,
    )
    def fail(self):
        pass

    def retry(self):
        pass


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
    amount = models.DecimalField(
        max_digits=8, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))]
    )
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
        """Setup new task for celery beat."""
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
        """Get crontab schedule object."""
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


class Notification(models.Model):
    """Model of notifications."""

    recipient = models.ForeignKey(
        'accounts.CustomUser',
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='receiver',
    )
    content = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now=True)
    url = models.CharField(max_length=255, null=True, blank=True)


class Loan(models.Model):
    """Model of Loans"""

    created_at = models.DateTimeField(auto_now=True)
    reason = models.CharField(max_length=255)
    lender = models.ForeignKey(
        'accounts.CustomUser',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='lender',
    )
    borrower = models.ForeignKey(
        'accounts.CustomUser',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='borrower',
    )
    amount = models.DecimalField(
        max_digits=8, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))]
    )
    payment_date = models.DateTimeField(null=True, blank=True)
    notify = models.OneToOneField(
        PeriodicTask,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    loan_state = FSMIntegerField(choices=LoanState.choices, default=LoanState.PENDING)

    @property
    def paid(self) -> Decimal:
        """Repaid loan amount."""
        payoff = Transaction.objects.filter(loan=self, state=TransactionState.ACCEPTED).aggregate(
            Sum('amount')
        )
        return payoff['amount__sum'] or 0

    @transition(
        field=loan_state,
        source=LoanState.PENDING,
        target=LoanState.GRANTED,
        conditions=[loan_funds_enough],
    )
    def grant(self):
        transaction = Transaction.objects.create(
            sender=self.lender,
            recipient=self.borrower,
            title=f'Pożyczka od {self.lender} dla {self.borrower}',
            amount=self.amount,
            types=TransactionType.LOAN,
        )
        if can_proceed(transaction.accept):
            transaction.accept()
            transaction.save()
        self.notify = PeriodicTask.objects.create(
            name=f'Payment notify {self.pk} ',
            task='loan_payment_date_notification',
            clocked=ClockedSchedule.objects.create(
                clocked_time=self.payment_date - datetime.timedelta(7),
            ),
            args=[self.payment_date, self.borrower.id, self.id],
            start_time=timezone.now(),
            one_off=True,
            enabled=True,
        )
        self.save()
        Notification.objects.create(
            recipient=self.borrower,
            content=f'Pożyczka na kwotę {self.amount} została przyznana, termin jej spłaty to {self.payment_date}',
        )

    @transition(field=loan_state, source=LoanState.PENDING, target=LoanState.DECLINED)
    def decline(self):
        Notification.objects.create(
            recipient=self.borrower,
            content=f'Pożyczka na kwotę {self.amount} została odrzucona.',
        )

    @transition(
        field=loan_state,
        source=[LoanState.GRANTED, LoanState.EXPIRED],
        target=LoanState.PAID,
        conditions=[is_paid],
    )
    def pay_off(self):
        Notification.objects.create(
            recipient=self.borrower,
            content=f'{self.borrower} spłacił pożyczkę z terminem spłaty do {self.payment_date}.',
        )

    @transition(field=loan_state, source=LoanState.GRANTED, target=LoanState.EXPIRED)
    def expire(self):
        Notification.objects.create(
            recipient=self.borrower,
            content=f'Termin spłaty pożyczki {self.payment_date} upłyną.',
        )
        self.notify.delete()
