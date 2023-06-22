from datetime import timezone
import hashlib
import random
from random import randint
from main.models import User
from django.core.exceptions import ObjectDoesNotExist

from main.models_.task_models import Task, Tasker
from main.utils.services import credit_finance


class TaskService:

    def generate_task_reference(name):
        """
        TO-DO: DOES NOT CHECK FOR DUPLICATE TASK NAME
        """

        # Generate a 4-digit random number
        number = random.randint(1000, 9999)
        reference = name + str(number)

        # Convert to MD5 hash
        task_reference = hashlib.md5(reference.encode()).hexdigest()

        return task_reference

    def get_completed_taskers(task_reference, user_reference):
        # Returns a list of users that have completed
        try:
            user = User.objects.get(reference=user_reference)
        except ObjectDoesNotExist:
            return {"success": False, "message": "user does not exist."}

        task_exists = Task.objects.filter(reference=task_reference).exists()

        if task_exists:
            task = Task.objects.get(reference=task_reference)
            completed_taskers = Tasker.objects.filter(user=user, task=task)
            tasker_list = [
                tasker.user.reference for tasker in completed_taskers]

            if len(tasker_list) < 1:
                return None
            return tasker_list

    def complete_task(task_reference, user_reference):
        try:
            user = User.objects.get(reference=user_reference)
        except ObjectDoesNotExist:
            return {"success": False, "message": "user does not exist."}

        message = {"success": True, "message": "Successfully completed task."}
        task_exists = Task.objects.filter(reference=task_reference).exists()

        if task_exists:
            task = Task.objects.get(reference=task_reference)
            tasker_exists = Tasker.objects.filter(
                user=user, task=task).exists()

            if task.expires_at > timezone.now():
                if tasker_exists:
                    tasker = Tasker.objects.get(
                        reference=task_reference, user=user)
                    if tasker.is_completed:
                        return {"success": True, "message": "Task already completed."}
                    task.taskers += 1
                    tasker.is_completed = True
                    tasker.save()
                    return message
                else:
                    Tasker.objects.create(
                        user=user, task=task, is_completed=True)

            else:
                return {"success": False, "message": "Task has expired."}
        else:
            return {"success": False, "message": "Invalid Task."}

    def commit_to_task(task_reference, user_reference):
        try:
            user = User.objects.get(reference=user_reference)
        except ObjectDoesNotExist:
            return {"success": False, "message": "user does not exist."}

        message = {"success": True,
                   "message": "Successfully committed to task."}
        task_exists = Task.objects.filter(reference=task_reference).exists()

        if task_exists:
            task = Task.objects.get(reference=task_reference)
            Tasker.objects.create(user=user, task=task, is_completed=False)
            status = credit_finance(user_reference, task.wager)
            if status.get('success'):
                return message
            return status

        else:
            return {"success": False, "message": "Invalid task reference"}
