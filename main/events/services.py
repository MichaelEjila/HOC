

from datetime import datetime
from main.models import User
from main.models_.event_models import Event, InvitedUser
from main.transaction.send_points.services import SendPointsService
from main.utils.constants import SendPointsConstant
from main.utils.services import bulk_reward, get_finance_user
from django.core.exceptions import ObjectDoesNotExist


class EventService:

    def get_attended_users(event):
        # Returns a list of users that have attended an event
        attended_users = InvitedUser.objects.filter(attended=True, event=event)
        user_references = [user.user.reference for user in attended_users]

        if len(user_references) < 1:
            return None
        return user_references

    def attend_event(event_reference, user):
        # Successfully scan the qr and attend the event
        message = {"success": True, "message": "Succesfully confirmed event"}

        event_exists = Event.objects.filter(reference=event_reference).exists()

        if event_exists:
            event = Event.objects.get(reference=event_reference)
            invited_user_exists = InvitedUser.objects.filter(
                event=event, user=user).exists()
            if event.expires_at > datetime.now().date():
                if invited_user_exists:
                    invited_user = InvitedUser.objects.get(
                        event=event, user=user)
                    invited_user.attended = True
                    invited_user.save()
                    return message
                else:
                    InvitedUser.objects.create(
                        event=event, user=user, attended=True, will_attend=False)
                    return message
            else:
                return {"success": False, "message": "Event has expired"}
        return {"success": False, "message": "Event does not exist"}

    def confirm_event(self, event_reference):
        # Confirm the event has finished
        message = {"success": True, "message": "Succesfully confirmed event"}

        event_exists = Event.objects.filter(reference=event_reference).exists()

        if event_exists:
            event = Event.objects.get(reference=event_reference)
            # get all the users that attended.
            attended_users = self.get_attended_users(event)
            if attended_users is not None:
                # for all the attendants, reward them.
                can_reward = bulk_reward(attended_users, event.event_reward)
                if can_reward.get("success") == True:
                    return message
                else:
                    return can_reward
            else:
                return {"success": False, "message": "No user attended this event"}

        else:
            return {"success": False, "message": "Event does not exist"}

    def book_event(event_reference, user_reference):
        # This is called when users click the 'I will attend" button
        try:
            user_obj = User.objects.get(reference=user_reference)
        except ObjectDoesNotExist:
            return {"success": False, "message": "User does not exist."}

        message = {"success": True, "message": "Succesfully booked event"}

        event_exists = Event.objects.filter(reference=event_reference).exists()
        invited_user_exists = InvitedUser.objects.filter(
            reference=event_reference, user=user_obj).exists()
        finance_user = get_finance_user()

        if finance_user is not None:

            if event_exists:
                event = Event.objects.get(reference=event_reference)
                if event.expires_at > datetime.now().date():
                    if invited_user_exists:
                        invited_user = InvitedUser.objects.get(
                            event=event, user=user_obj)
                        invited_user.will_attend = True
                        invited_user.save()

                    else:
                        InvitedUser.objects.create(
                            event=event, user=user_obj, attended=False, will_attend=True)
                        return message

                    can_send_points = SendPointsService.send_points(
                        user_obj.reference, finance_user.reference, event.wager, mode=SendPointsConstant.DIRECT)
                    if can_send_points.get("success") == True:
                        return message
                    else:
                        return can_send_points
                else:
                    return {"success": False, "message": "Event has expired"}

            else:
                return {"success": False, "message": "Event does not exist"}

        else:
            return {"success": False, "message": "Finance account is not active"}
