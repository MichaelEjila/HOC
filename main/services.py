import random
from random import randint
from django.utils.text import slugify
import hashlib
import datetime

from django.contrib.auth import get_user_model
User = get_user_model


class VendorService():

    def generate_vendor_id():
        prefix = 'vendor'
        while True:
            random_number = randint(10000, 99999)
            vendor_id = f'{prefix}{random_number}'
            if not User.objects.filter(vendor_id=vendor_id).exists():
                return vendor_id
            

class UserRegistrationService():

    def generate_reference(name, model=None):
        """
        TO-DO: DOES NOT CHECK FOR DUPLICATE OBJECT NAME
        """

        # if not model.objects.filter(name=name).exist():
        #     return {"message": "Object exists"}

        # Generate a 4-digit random number
        number = random.randint(1000, 9999)
        reference = name + str(number)

        # Convert the full name with the number to MD5 hash
        task_reference = hashlib.md5(reference.encode()).hexdigest()

        return task_reference

    def generate_auto_username(first_name, last_name):
        # Concatenate the first name and last name
        username = slugify(first_name + last_name)

        # Generate a four-digit random number
        number = random.randint(1000, 9999)

        # Shuffle the number
        shuffled_number = ''.join(random.sample(str(number), len(str(number))))

        # Concatenate the shuffled number with the username
        username += shuffled_number

        return username


    def generate_user_reference(first_name, last_name):
        # Concatenate the first name and last name
        full_name = first_name + last_name

        # Generate a 4-digit random number
        number = random.randint(1000, 9999)

        # Add the random number to the full name
        full_name_with_number = full_name + str(number)

        # Convert the full name with the number to MD5 hash
        reference = hashlib.md5(full_name_with_number.encode()).hexdigest()

        return reference

    def generate_card_reference(card_id):

        card_reference = hashlib.md5(card_id.encode()).hexdigest()

        return card_reference
    
    def generate_transaction_reference(sender, recipient, amount):
        # Concatenate the sender and receivers names and amoubt
        full_details = sender + recipient +str(amount)

        # Get the current date and time
        now = datetime.datetime.now()

        # Format the current date and time as ra string
        current_datetime = now.strftime("%Y%m%d%H%M%S")

        # Concatenate the formatted date and time with the full name
        raw_transaction_reference = full_details + current_datetime

        # Convert the full name with the date and time to MD5 hash
        transaction_reference = hashlib.md5(raw_transaction_reference.encode()).hexdigest()

        return transaction_reference
    
    def generate_ticket_reference(sender, amount):
        # Concatenate the sender name and amount
        full_details = sender + str(amount)

        # Get the current date and time
        now = datetime.datetime.now()

        # Format the current date and time as ra string
        current_datetime = now.strftime("%Y%m%d%H%M%S")

        # Concatenate the formatted date and time with the full name
        raw_transaction_reference = full_details + current_datetime

        # Convert the full name with the date and time to MD5 hash
        transaction_reference = hashlib.md5(raw_transaction_reference.encode()).hexdigest()

        return transaction_reference
    
    def generate_club_card_reference(user):
        prefix = 'EUNUESA'
        id = user.id
        card_id = prefix + str(id)

        card_reference = hashlib.md5(card_id.encode()).hexdigest()

        return {"card_id":card_id, "reference":card_reference}






