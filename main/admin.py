from django.contrib import admin
from django import forms
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from main.events.services import EventService
from main.models import Card, PendingTicket, Transaction, User
from main.models_.event_models import Event, InvitedUser
from main.models_.task_models import Task, Tasker
from main.services import UserRegistrationService, VendorService
from main.tasks.services import TaskService
from django.core.exceptions import ValidationError
from django.contrib.auth.hashers import make_password
from main.utils.constants import CLUB_REFERENCE, DIAMOND_REFERENCE

from main.utils.services import bulk_reward


class UserCreationForm(forms.ModelForm):
    password1 = forms.CharField(
        label='Password', widget=forms.PasswordInput(attrs={'minlength': '5'}))
    password2 = forms.CharField(
        label='Confirm Password', widget=forms.PasswordInput(attrs={'minlength': '5'}))
    username = forms.CharField(widget=forms.HiddenInput(), required=False)
    matric_number = forms.CharField(required=False)

    class Meta:
        model = User
        fields = '__all__'
        exclude = ['username']

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords do not match.")
        return password2


class CustomUserAdmin(BaseUserAdmin):
    # Specify the fields to display in the admin list view
    list_display = ['first_name', 'last_name', 'matric_number', 'user_category',
                    'vendor_id', 'balance', 'username', 'is_staff', 'is_active', ]

    # Specify the fields to include in the admin detail view
    fieldsets = (
        (None, {'fields': ('username', 'reference',
         'user_category', 'vendor_id', 'balance')}),
        ('Personal Info', {'fields': ('first_name', 'last_name')}),
        # ('Permissions', {'fields': ('is_active', 'is_staff', 'groups', 'user_permissions')}),
        ('Permissions', {
         'fields': ('is_active', 'is_staff', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('first_name', 'last_name', 'matric_number', 'user_category', 'password1', 'password2', 'is_active'),
        }),
    )

    # Specify the filter options for the admin list view
    list_filter = ['is_staff', 'is_active']

    # Specify the search fields for the admin list view
    search_fields = ['first_name', 'last_name', 'matric_number__endswith',
                     'username', 'email', 'matric_number', 'reference', 'user_category']

    add_form = UserCreationForm

    readonly_fields = ('balance', 'username', 'reference', 'vendor_id', )

    def get_form(self, request, obj=None, **kwargs):
        if obj is None:
            # For adding new users
            kwargs['form'] = self.add_form
        return super().get_form(request, obj, **kwargs)

    def save_model(self, request, obj, form, change):
        if not change:
            obj.reference = UserRegistrationService.generate_user_reference(
                obj.first_name, obj.last_name)
            # Set a password
            obj.password = make_password(form.cleaned_data['password2'])
            obj.username = obj.reference

        if obj.user_category == 'vendor':
            # Generate and assign the vendor ID
            obj.vendor_id = VendorService.generate_vendor_id()
        else:
            # The user is a student, allow manual input of the matric number
            pass

        super().save_model(request, obj, form, change)

        if not Card.objects.filter(user=obj).exists():

            card_obj = Card.objects.create(user=obj)
            card_obj.save()


class CardAdmin(admin.ModelAdmin):
    list_display = ['get_user_full_name', 'reference', 'card_id',
                    'type', 'get_user_balance', 'get_user_matric_number', 'is_active']
    raw_id_fields = ['user']

    def get_user_full_name(self, obj):
        return obj.user.get_full_name()

    def get_user_reference(self, obj):
        return obj.user.reference

    def get_user_matric_number(self, obj):
        return obj.user.matric_number

    def get_user_balance(self, obj):
        return obj.user.balance

    get_user_full_name.short_description = 'Full Name'
    get_user_reference.short_description = 'User Reference'
    get_user_matric_number.short_description = 'Matric Number'
    get_user_balance.short_description = 'Balance'

    def get_readonly_fields(self, request, obj=None):
        if obj:  # Editing an existing object
            return ['reference', 'user', 'card_id']
        else:  # Adding a new object
            return ['reference', 'card_id']

    def save_model(self, request, obj, form, change):
        if not change and not obj.card_id:
            if obj.type == 'diamond':
                card_count = Card.objects.filter(type='diamond').count()
                obj.card_id = f"EUNUD{str(card_count + 1).zfill(3)}"
                if obj.card_id in DIAMOND_REFERENCE:
                    obj.reference = DIAMOND_REFERENCE[obj.card_id]
            elif obj.type == 'club':
                card_count = Card.objects.filter(type='club').count()
                obj.card_id = f"EUNUc{str(card_count + 1).zfill(3)}"
                if obj.card_id in CLUB_REFERENCE:
                    obj.reference = CLUB_REFERENCE[obj.card_id]

        elif change and 'type' in form.changed_data and form.cleaned_data['type'] == 'club':
            card_count = Card.objects.filter(type='club').count()
            obj.card_id = f"EUNUc{str(card_count + 1).zfill(3)}"
            if obj.card_id in CLUB_REFERENCE:
                obj.reference = CLUB_REFERENCE[obj.card_id]

        super().save_model(request, obj, form, change)


class TransactionAdmin(admin.ModelAdmin):
    # Specify the fields to display in the admin list view
    list_display = ['transaction_reference', 'created_at', 'amount',
                    'senders_hash', 'recipients_hash', 'senders_new_balance']

    # Disable the ability to add new transactions
    def has_add_permission(self, request):
        return False

    # Disable the ability to change existing transactions
    def has_change_permission(self, request, obj=None):
        return False


class PendingTicketAdmin(admin.ModelAdmin):
    # Specify the fields to display in the admin list view
    list_display = ['reference', 'created_at', 'mode',
                    'amount', 'senders_hash', 'number_of_receivers']

    # Disable the ability to add new pending tickets
    def has_add_permission(self, request):
        return False

    # Disable the ability to change existing pending tickets
    def has_change_permission(self, request, obj=None):
        return False


class TaskAdmin(admin.ModelAdmin):
    # Specify the fields to display in the admin list view
    list_display = ['task_name', 'reference', 'created_at',
                    'expires_at', 'prize', 'is_completed', 'taskers']

    def get_readonly_fields(self, request, obj=None):
        if obj:  # Editing an existing object
            return ['reference']
        else:  # Adding a new object
            return ['reference']

    def save_model(self, request, obj, form, change):
        if not change:  # Adding a new object
            # Generate the card reference and assign the card ID
            task_reference = TaskService.generate_task_reference(obj.task_name)
            obj.reference = task_reference

        super().save_model(request, obj, form, change)


class TaskAdmin(admin.ModelAdmin):
    # Specify the fields to display in the admin list view
    list_display = ['task_name', 'reference', 'created_at',
                    'expires_at', 'prize', 'is_completed', 'taskers']

    def get_readonly_fields(self, request, obj=None):
        if obj:  # Editing an existing object
            return ['reference']
        else:  # Adding a new object
            return ['reference']

    def save_model(self, request, obj, form, change):
        if not change:  # Adding a new object
            # Generate the card reference and assign the card ID
            task_reference = TaskService.generate_task_reference(obj.task_name)
            obj.reference = task_reference
        else:
            if obj.is_completed:
                completed_taskers = Tasker.objects.filter(task=obj)
                tasker_list = [
                    tasker.user.reference for tasker in completed_taskers]

                if len(tasker_list) > 1:
                    reward = bulk_reward(tasker_list, obj.prize)
                    if not reward.get('success'):
                        raise ValidationError(reward.get('message'))

        super().save_model(request, obj, form, change)


class EventAdmin(admin.ModelAdmin):
    # Specify the fields to display in the admin list view
    list_display = ['name', 'reference', 'time', 'event_wager',
                    'attendees', 'is_completed', 'attendees']

    def get_readonly_fields(self, request, obj=None):
        if obj:  # Editing an existing object
            return ['reference']
        else:  # Adding a new object
            return ['reference']

    def save_model(self, request, obj, form, change):
        if not change:  # Adding a new object
            # Generate the card reference and assign the card ID
            event_reference = TaskService.generate_task_reference(obj.name)
            obj.reference = event_reference
        else:
            if obj.is_completed == True:
                attendance = EventService.get_attended_users(obj)
                if attendance is not None:
                    confirm_event = EventService.confirm_event(obj)

        super().save_model(request, obj, form, change)


admin.site.register(User, CustomUserAdmin)
admin.site.register(Transaction, TransactionAdmin)
admin.site.register(PendingTicket, PendingTicketAdmin)
admin.site.register(Card, CardAdmin)
admin.site.register(Task, TaskAdmin)
admin.site.register(Tasker)
admin.site.register(Event, EventAdmin)
admin.site.register(InvitedUser)
