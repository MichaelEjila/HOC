import hashlib
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.forms import ValidationError

from main.services import UserRegistrationService
from django.utils import timezone
from main.utils.constants import CARD_TYPES, CLUB_REFERENCE, DIAMOND_REFERENCE, MODE, TRANSACTION_TYPES, USER_CATEGORY
from main.utils.validators import UserValidator


class User(AbstractUser):
    matric_number = models.CharField(max_length=13, null=True, unique=True, validators=[
                                     UserValidator.validate_matric_number])
    user_category = models.CharField(
        help_text='Type of User',  max_length=200, choices=USER_CATEGORY)
    balance = models.DecimalField(
        help_text='Users Points Balance', decimal_places=2, max_digits=16, default=0.00
    )
    reference = models.CharField(
        help_text='User Reference', max_length=200, unique=True)
    vendor_id = models.CharField(
        help_text='Vendor ID',
        max_length=200,
        null=True,
        unique=True
    )

    def __str__(self):
        return self.get_full_name()

    def clean(self):
        super().clean()
        if self.user_category == 'student' and not self.matric_number:
            raise ValidationError(
                {'matric_number': 'Matric number is required for student users.'})

    def save(self, *args, **kwargs):
        if self.user_category == 'student':
            self.vendor_id = None

        elif self.user_category == 'vendor':
            self.matric_number = None

        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        if self.balance != 0:
            # User balance is not zero, prevent deletion
            return
        super().delete(*args, **kwargs)


class Transaction(models.Model):
    transaction_type = models.CharField(
        max_length=10, choices=TRANSACTION_TYPES)
    transaction_reference = models.CharField(max_length=200, unique=True)
    created_at = models.DateTimeField(
        default=timezone.now, help_text='Time transaction was initiated')
    amount = models.DecimalField(
        help_text="Amount of point being sent", decimal_places=2, max_digits=16, default=0.00
    )
    senders_hash = models.CharField(max_length=200)
    recipients_hash = models.CharField(max_length=200)
    senders_new_balance = models.DecimalField(
        help_text="Senders New Balance", decimal_places=2, max_digits=16, default=0.00
    )

    def __str__(self):
        return self.transaction_reference


class PendingTicket(models.Model):
    reference = models.CharField(
        help_text='Ticket Transaction', max_length=200, unique=True)
    created_at = models.DateTimeField(default=timezone.now)
    mode = models.CharField(max_length=25, choices=MODE)
    amount = models.DecimalField(
        help_text="", decimal_places=2, max_digits=16, default=0.00
    )
    senders_hash = models.CharField(max_length=200)
    number_of_receivers = models.IntegerField(default=1)


class Card(models.Model):
    user = models.OneToOneField(
        User, related_name="user_card", on_delete=models.CASCADE)
    reference = models.CharField(
        help_text='Card Reference', max_length=200, unique=True)
    type = models.CharField(
        max_length=25, choices=CARD_TYPES, default='diamond')
    card_id = models.CharField(help_text='Card ID', max_length=25, unique=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.user.get_full_name() + "'s Card"

    def save(self, *args, **kwargs):
        if not self.pk:
            if self.type == 'diamond':
                card_count = Card.objects.filter(type='diamond').count()
                card_id = f"EUNUD{str(card_count + 1).zfill(3)}"
            elif self.type == 'club':
                card_count = Card.objects.filter(type='club').count()
                card_id = f"EUNUc{str(card_count + 1).zfill(3)}"
            else:
                card_id = ''

            self.card_id = card_id
            if self.card_id in DIAMOND_REFERENCE:
                self.reference = DIAMOND_REFERENCE[self.card_id]
            elif self.card_id in CLUB_REFERENCE:
                self.reference = CLUB_REFERENCE[self.card_id]
        super().save(*args, **kwargs)
