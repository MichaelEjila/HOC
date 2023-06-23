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
from django.db.models import Q

from main.utils.services import get_finance_user


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
        password = request.POST.get('password')
        card_exists = Card.objects.filter(reference=card_reference).exists()
        if card_exists:
            card = Card.objects.get(reference=card_reference)
            user = authenticate(
                username=card.user.reference, password=password)

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
            event_validity = EventService.attend_event(reference, request.user)
            task_validity = TaskService.complete_task(
                reference, request.user.reference)
            if event_validity.get("success"):
                message = event_validity.get("message")
                error_message = {"status": False, "message": message}
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

            elif task_validity.get("success"):
                message = task_validity.get("message")
                error_message = {"status": False, "message": message}
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

            else:
                error_message = {"status": True,
                                 "message": event_validity.get("message")}
                transaction_validity = SendPointsService.confirm_pending_tickets(
                    reference, request.user.reference)

                if transaction_validity.get("success"):
                    message = transaction_validity.get("message")
                    error_message = {"status": False, "message": message}
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

                else:
                    error_message = {
                        "status": True, "message": transaction_validity.get("message")}

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

        elif matric_number and amount:
            # Perform the send directly logic using the "reference" value
            # get reference or matric number
            # pull recipient account and initiate send points
            if len(matric_number) > 3:
                user_exists = User.objects.filter(reference=reference).exists(
                ) or User.objects.filter(matric_number__endswith=matric_number).exists()

                if user_exists:
                    try:
                        recipient = User.objects.get(reference=reference)
                    except User.DoesNotExist:
                        try:
                            recipient = User.objects.get(
                                matric_number__endswith=matric_number)
                        except User.DoesNotExist:
                            try:
                                recipient = User.objects.get(
                                    vendor_id=matric_number)
                            except User.DoesNotExist:
                                error_message = {"status": True,
                                                 "message": "Invalid Details"}
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

                    status = SendPointsService.send_points(
                        request.user.reference, recipient.reference, amount, SendPointsConstant.DIRECT)
                    if status.get("success"):
                        message = status.get("message")
                        error_message = {"status": False, "message": message}
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
                    else:
                        error_message = {"status": True,
                                         "message": status.get("message")}

                error_message = {"status": True,
                                 "message": "Invalid Credentials"}
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
            else:
                error_message = {"status": True, "message": "Invalid Details"}
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

        elif amount is not None and matric_number is None:
            user = request.user
            ticket_validity = SendPointsService.create_ticket(user, amount)
            if ticket_validity.get('success') == True:
                message = ticket_validity.get('message')
                error_message = {"status": False, "message": message}
                ticket_obj = PendingTicket.objects.filter(
                    senders_hash=request.user.reference).latest('created_at')
                qr_hash = ticket_obj.reference

            # Update the context dictionary with all the required variables
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


def transaction_view(request):
    # Debit - amount, where, date and time
    # Credit - amount, from, date and time
    error_message = {"status": False, "message": "No errors"}
    user = request.user
    transactions = Transaction.objects.filter(
        Q(senders_hash=user.reference) | Q(recipients_hash=user.reference),
        transaction_type__in=["debit", "credit"]
    ).order_by('-created_at')
    recipients_names = [User.objects.get(
        reference=transaction.recipients_hash).get_full_name() for transaction in transactions]
    senders_names = [User.objects.get(
        reference=transaction.senders_hash).get_full_name() for transaction in transactions]

    transactions_with_names = zip(
        transactions, recipients_names, senders_names)

    context = {
        "transactions_with_names": transactions_with_names,
        'error_message': error_message,
        'user': user
    }

    return render(request, "trans.html", context)


def task_view(request):
    error_message = {"status": False, "message": "No errors"}
    message = ''
    # Retrieve all tasks
    tasks = Task.objects.all()

    # Get the number of open tasks
    number_of_tasks = tasks.count()

    # Create a list to store task details
    task_list = []

    # Iterate over each task
    for task in tasks:
        # Get the tasker object for the current user and task (if it exists)
        tasker = Tasker.objects.filter(user=request.user, task=task).first()

        # Check if the tasker object exists and get the completion status
        if tasker:
            is_completed = tasker.is_completed
        else:
            is_completed = False

        # Create a dictionary with task details
        task_details = {
            'task_name': task.task_name,
            'description': task.description,
            'prize': task.prize,
            'is_completed': is_completed,
            'error_message': error_message,
            'message': message
        }

        # Add the task details to the list
        task_list.append(task_details)

    # Create the context dictionary
    context = {
        'number_of_tasks': number_of_tasks,
        'task_list': task_list,
        'error_message': error_message,
        'message': message
    }

    # Render the template with the context
    return render(request, 'tasks.html', context)


def armstrongs_world(request):
    # Return everything this nigga wants.
    # implenting attending of attendees (he just means 10 out of 30)
    if request.user.is_superuser:
        error_message = {"status": False, "message": "No errors"}
        message = ''
        number_of_users = User.objects.all()
        number_of_diamond_cards = Card.objects.filter(card_type='diamond')
        number_of_club_cards = Card.objects.filter(card_type='club')
        active_tasks = Task.objects.filter(is_completed=False)
        number_of_pending_tickets = PendingTicket.objects.all()

        finance_user = get_finance_user()
        if finance_user is not None:
            amount = request.POST.get('amount')
            password = request.POST.get('password')
            authenticated_user = authenticate(
                username=finance_user.username, password=password)

            if authenticated_user is not None:
                finance_user.balance += amount
                message = "Succesfully Injected points"
            else:
                error_message = {"status": True,
                                 "message": "Invalid Credentials"}

        else:
            error_message = {"status": True,
                             "message": "Finance user not set up"}

        context = {
            'error_message': error_message,
            'message': message,
            'number_of_users': number_of_users,
            'number_of_diamond_cards': number_of_diamond_cards,
            'number_of_club_cards': number_of_club_cards,
            'active_tasks': active_tasks,
            'number_of_pending_tickets': number_of_pending_tickets,

        }

        return render(request, 'flourish.html', context)

    else:
        error_message = {"status": True, "message": "Not Authenticated"}
        context = {
            'error_message': error_message,

        }

        return render(request, 'flourish.html', context)
