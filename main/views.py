from datetime import timedelta
from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from main.events.services import EventService
from main.models import Card, PendingTicket, Transaction, User
from django.utils import timezone


from main.models_.event_models import Event
from main.models_.task_models import Task, Tasker
from main.qr.services import QrGenerator
from main.tasks.services import TaskService
from main.transaction.send_points.services import SendPointsService
from main.utils.constants import SendPointsConstant
from django.contrib.auth.decorators import login_required


def index(request):
    error_message = {"status": False, "message": "No errors"}
    is_authenticated = True
    first_name = ''
    last_name = ''
    matric_number = ''
    card_type = ''
    open_tickets_count = ''
    if not request.user.is_authenticated:
        is_authenticated = False
    else:
        user = request.user
        first_name = user.first_name
        last_name = user.last_name
        matric_number = user.matric_number
        # Calculate the time threshold (1 hour ago)
        time_threshold = timezone.now() - timedelta(hours=1)

        # Query the PendingTicket objects for the user within the time threshold
        open_tickets = PendingTicket.objects.filter(
            senders_hash=request.user, created_at__gte=time_threshold)

        # Get the count of the open tickets
        open_tickets_count = open_tickets.count()
        card_exists = Card.objects.filter(user=user).exists()

        if card_exists:
            card = Card.objects.get(user=user)
            card_type = card.type
        else:
            card_type = "No card"

    if request.method == 'POST':
        card_reference = request.POST.get('qr_code')
        pin = request.POST.get('password')
        card_exists = Card.objects.filter(reference=card_reference).exists()
        if card_exists:
            card = Card.objects.get(reference=card_reference)
            user = authenticate(username=card.user.username, password=pin)

            if user is not None:
                login(request, user)
                is_authenticated = True

                first_name = user.first_name
                last_name = user.last_name
                matric_number = user.matric_number
                # Calculate the time threshold (1 hour ago)
                time_threshold = timezone.now() - timedelta(hours=1)

                # Query the PendingTicket objects for the user within the time threshold
                open_tickets = PendingTicket.objects.filter(
                    senders_hash=request.user, created_at__gte=time_threshold)

                # Get the count of the open tickets
                open_tickets_count = open_tickets.count()
                card_exists = Card.objects.filter(user=user).exists()

                if card_exists:
                    card = Card.objects.get(user=user)
                    card_type = card.type
                else:
                    card_type = "No card"

                context = {
                    'first_name': first_name,
                    'last_name': last_name,
                    'matric_number': matric_number,
                    'card_type': card_type,
                    'open_tickets_count': open_tickets_count,
                    'error_message': error_message,
                    'is_authenticated': is_authenticated
                }

                return render(request, 'login.html', context)

            else:
                error_message = {"status": True,
                                 "message": "Invalid Credentials"}
                return render(request, 'login.html', {'error_message': error_message, 'is_authenticated': is_authenticated})
        else:
            error_message = {"status": True, "message": "Invalid Credentials"}
            return render(request, 'login.html', {'error_message': error_message, 'is_authenticated': is_authenticated})

    context = {
        'first_name': first_name,
        'last_name': last_name,
        'matric_number': matric_number,
        'card_type': card_type,
        'open_tickets_count': open_tickets_count,
        'error_message': error_message,
        'is_authenticated': is_authenticated
    }

    return render(request, 'login.html', context)


@login_required
def trivia_view(request):

    # show events
    # if user will attend
    # take event wager from their stingy hand
    # if user is attending
    # reward the sure guy
    error_message = {"status": False, "message": "No errors"}
    if request.user.is_authenticated:
        events = Event.objects.all()

        if request.method == 'POST':
            event_reference = request.POST.get('event_reference')
            event_exists = Event.objects.filter(
                reference=event_reference).exists()

            if event_exists:
                event = Event.objects.get(reference=event_reference)

                if not event.is_completed:
                    event.will_attend = True
                    event.save()

                # Redirect to the same view after updating the field
                return redirect('trivia_view')

            else:
                error_message = {'status': True,
                                 "message": "Event does not exist"}

        else:
            context = {
                'events': events,
                'error_message': error_message
            }

            return render(request, 'trivia.html', context)
    is_authenticated = False
    return render(request, 'login.html', {'error_message': error_message, "is_authenticated": is_authenticated})


def account_view(request):
    # shows balance, name, car
    # migrate card, show open ticket, scan open tickets/events, send directly to matric
    error_message = {"status": False, "message": "No errors"}
    message = ''
    user = request.user
    qr_hash = ''
    card_exists = Card.objects.filter(user=user).exists()
    if card_exists:
        card = Card.objects.get(user=user)
        card_type = card.type
    else:
        card_type = "No card"

    balance = user.balance
    first_name = user.first_name
    last_name = user.last_name
    current_time = timezone.now()
    one_hour_ago = current_time - timezone.timedelta(hours=1)
    pending_tickets = PendingTicket.objects.filter(
        senders_hash=user.username, created_at__gte=one_hour_ago)

    if request.method == "POST":
        reference = request.POST.get("scan_ticket")
        matric_number = request.POST.get("matric_number")
        amount = request.POST.get("amount")

        if reference is not None:

            # Perform the scan tickets logic using the "reference" value
            # get reference check if it's an event and confirm the event
            # if it's not check if it's a valid pending ticket and confirm the ticket
            event_validity = EventService.attend_event(reference, request.user)
            task_validity = TaskService.complete_task(
                reference, request.user.reference)
            if event_validity.get("success"):
                message = event_validity.get("message")
                error_message = {"status": False, "message": message}
                return redirect('account_view')
            elif task_validity.get("success"):
                message = task_validity.get("message")
                error_message = {"status": False, "message": message}
                return redirect('account_view')

            else:
                error_message = {"status": True,
                                 "message": event_validity.get("message")}
                transaction_validity = SendPointsService.confirm_pending_tickets(
                    reference, request.user.reference)

                if transaction_validity.get("success"):
                    message = transaction_validity.get("message")
                    error_message = {"status": False, "message": message}
                    return redirect('account_view')
                else:
                    error_message = {
                        "status": True, "message": transaction_validity.get("message")}
                    return redirect('account_view')

        elif (matric_number and amount) is not None:
            # Perform the send directly logic using the "reference" value
            # get reference or matric number
            # pull recipient account and initiate send points
            user_exists = User.objects.filter(reference=reference).exists(
            ) or User.objects.filter(matric_number__endswith=matric_number).exists()
            breakpoint()
            if user_exists:
                breakpoint()
                try:
                    recipient = User.objects.get(reference=reference)
                except User.DoesNotExist:
                    recipient = User.objects.get(matric_number=matric_number)

                status = SendPointsService.send_points(
                    request.user, recipient, amount, SendPointsConstant.DIRECT)
                if status.get("success"):
                    message = status.get("message")
                    error_message = {"status": False, "message": message}
                    return redirect('account_view')
                else:
                    breakpoint()
                    error_message = {"status": True,
                                     "message": status.get("message")}

            error_message = {"status": True, "message": "Invalid Credentials"}
            return redirect('account_view')

        elif (amount is not None) and (matric_number is None):
            user = request.user
            ticket_validity = SendPointsService.create_ticket(user, amount)
            if ticket_validity.get('success') == True:
                message = ticket_validity.get('message')
                error_message = {"status": False, "message": message}
                ticket_obj = PendingTicket.objects.filter(
                    senders_hash=request.user.reference).latest('created_at')
                qr_hash = ticket_obj.reference
                context = {
                    'first_name': first_name,
                    'last_name': last_name,
                    'balance': balance,
                    'card_type': card_type,
                    'pending_tickets': pending_tickets,
                    'error_message': error_message,
                    'qr_hash': qr_hash,
                }
                return render(request, "account.html", context)

            error_message = {"status": True,
                             "message": ticket_validity.get('message')}
            return redirect('account_view')

            # taking amount, user details
            # produce pending ticket for that transaction
            # whoever confirms pending ticket is the recipient

        # elif action == 'migrate card':
        #     pass

    context = {
        'first_name': first_name,
        'last_name': last_name,
        'balance': balance,
        'card_type': card_type,
        'pending_tickets': pending_tickets,
        'error_message': error_message,
        'qr_hash': qr_hash,
        'message': message,
    }

    return render(request, "account.html", context)


def transaction_view(request):
    # Debit - amount, where, date and time
    # Credit - amount, from, date and time
    error_message = {"status": False, "message": "No errors"}
    user = request.user
    transactions = Transaction.objects.filter(senders_hash=user.reference, transaction_type__in=[
                                              "debit", "credit"]).order_by('-created_at')

    context = {
        "transactions": transactions,
        'error_message': error_message,
    }

    return render(request, "trans.html", context)


def task_view(request):
    # Returns all tasks
    # complete tasks
    # return number of open tasks
    error_message = {"status": False, "message": "No errors"}
    user = request.user
    tasks = Task.objects.all()
    completed_tasks = Tasker.objects.filter(
        user=user, is_completed=True).values_list('task_id', flat=True)

    task_list = []
    for task in tasks:
        is_completed = task.id in completed_tasks
        task_data = {
            'task': task,
            'is_completed': is_completed
        }
        task_list.append(task_data)

    context = {
        'task_list': task_list,
        'number_of_tasks': len(tasks),
        'error_message': error_message,
    }

    return render(request, 'tasks.html', context)


def armstrongs_world(request):
    # Return everything this nigga wants.
    # implenting attending of attendees (he just means 10 out of 30)
    error_message = {"status": False, "message": "No errors"}
    pass
