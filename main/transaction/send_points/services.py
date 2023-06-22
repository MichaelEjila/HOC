from main.models import PendingTicket, Transaction
import datetime
from main.models_.event_models import Event
from main.utils.constants import SendPointsConstant
from main.services import UserRegistrationService
from django.contrib.auth import get_user_model
User = get_user_model()


class SendPointsService():
    
    def send_points(sender, recipient, amount, mode=SendPointsConstant.DIRECT):
        message = {"success":True, "message":"Succesfully sent points"}

        if sender.balance >= amount:

            if mode == SendPointsConstant.DIRECT:
                
                transaction_reference = UserRegistrationService.generate_transaction_reference(sender, recipient, amount)

                sender.balance -= amount
                recipient.balance += amount
                Transaction.objects.create(
                    reference=transaction_reference,
                    created_at = datetime.datetime.now(),
                    amount = amount,
                    senders_hash = sender.reference,
                    recipient_hash = recipient.reference,
                    senders_new_balance = sender.balance
                    )
                return message
            
        else:
            return {"success":False, "message":"Insufficient funds."}
        
    def create_ticket(sender, amount, ticket_mode='single', **kwargs):
        message = {"success":True, "message":"Succesfully created ticket"}
        sender_exists = User.objects.filter(reference=sender).exists()

        if sender_exists:

                if ticket_mode == 'single':
                    transaction_reference = UserRegistrationService.generate_ticket_reference(sender.reference, amount)
                    PendingTicket.objects.create(
                        reference=transaction_reference,
                        mode = 'single',
                        amount = amount,
                        senders_hash = sender.reference,
                        number_of_receivers = 1
                        )
                    return message
                    
                elif ticket_mode == 'multiple':
                    number_of_receivers = kwargs.get("number_of_receivers")

                    transaction_reference = UserRegistrationService.generate_transaction_reference(sender, amount)
                    PendingTicket.objects.create(
                        reference=transaction_reference,
                        mode = 'multiple',
                        amount = amount,
                        senders_hash = sender.reference,
                        number_of_receivers = number_of_receivers,
                        )
                    return message
                
        return {"success":False, "message":"Sender does not exist"}
        

    def confirm_pending_tickets(reference, recipient):
        message = {"success":True, "message":"Succesfully sent points"}
        pending_ticket_exists = PendingTicket.objects.filter(reference=reference).exists()

        if pending_ticket_exists:
            ticket_obj = PendingTicket.objects.get(reference=reference)
            sender = User.objects.get(reference=ticket_obj.senders_hash)
            amount = ticket_obj.amount

            if sender.balance >= amount:

                sender.balance -= amount
                recipient.balance += amount
                Transaction.objects.create(
                    transaction_reference=reference,
                    created_at = datetime.datetime.now(),
                    amount = amount,
                    senders_hash = sender.reference,
                    recipient_hash = recipient.reference,
                    senders_new_balance = sender.balance
                    )
                PendingTicket.objects.filter(reference=reference).delete()
                return message
            
            else:
                return {"success":False, "message":"Insufficient points"}
                
        else:
            return {"success":False, "message":"Invalid reference"}