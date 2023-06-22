from django.db import models
from django.utils import timezone
from main.models import User
from django.core.exceptions import ValidationError
from main.utils.services import reward_user

class Task(models.Model):
    task_name = models.CharField(help_text = 'Task Name', max_length=200, unique=True)
    description = models.CharField(help_text = 'Task Description', max_length=200, unique=True)
    reference = models.CharField(help_text = 'Task Reference', max_length=200, unique=True)
    created_at = models.DateTimeField(default=timezone.now)
    expires_at = models.DateTimeField(default=timezone.now)
    wager = models.DecimalField(
        help_text = 'What user stakes for a task', decimal_places=2, max_digits=16, default=0.00
        )
    prize = models.DecimalField(
        help_text = 'Users Points Balance', decimal_places=2, max_digits=16, default=0.00
        )
    is_completed = models.BooleanField(default=False)
    taskers = models.IntegerField(help_text="No of users that have completed a task", default=0)

    def __str__(self):
        return self.task_name


class Tasker(models.Model):
    class Meta:
        verbose_name = 'Tasker'
        verbose_name_plural = 'Taskers'

    user = models.ForeignKey(User, related_name="tasker", on_delete=models.CASCADE)
    task = models.ForeignKey(Task, related_name="taskers_task", on_delete=models.CASCADE)
    is_completed = models.BooleanField(default=False)

    def __str__(self):
        return self.user.get_full_name() 
    
    def save(self, *args, **kwargs):
        if self.is_completed:
            status = reward_user(self.user.user_reference, self.task.prize)
            if status.get('success'):
                self.delete()
            else:
                raise ValidationError(status.get('message'))
            
        else:
            super().save(*args, **kwargs)