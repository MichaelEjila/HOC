from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model
User = get_user_model()

class Event(models.Model):
    name = models.CharField(help_text = 'Event Name', max_length=200, unique=True)
    reference = models.CharField(help_text = 'Event Reference', max_length=200, unique=True)
    time = models.DateTimeField(default=timezone.now)
    expires_at = models.DateField(default=timezone.now)
    event_wager = models.DecimalField(
        help_text = 'Amount to be deducted if you choose to attend', decimal_places=2, max_digits=16, default=0.00
        )
    event_reward = models.DecimalField(
        help_text = 'Reward for attending events', decimal_places=2, max_digits=16, default=0.00
        )
    attendees = models.IntegerField(help_text="No of users that are attending an event", default=0)
    is_completed = models.BooleanField(default=False)

    def __str__(self):
        return self.name

class InvitedUser(models.Model):
    class Meta:
        verbose_name = 'Invited User'
        verbose_name_plural = 'Invited Users'

    user = models.ForeignKey(User, related_name="event_attendees", on_delete=models.CASCADE)
    event = models.ForeignKey(Event, related_name="event_name", on_delete=models.CASCADE)
    attended = models.BooleanField(default=False, help_text="If user has attended Event", )
    will_attend = models.BooleanField(default=False, help_text="If user plans to attend")

    def __str__(self):
        return self.user.get_username()