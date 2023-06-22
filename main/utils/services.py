import os
from django.contrib.auth import get_user_model

from main.transaction.send_points.services import SendPointsService
from main.utils.constants import SendPointsConstant
from django.core.exceptions import ObjectDoesNotExist
User = get_user_model()

def get_finance_user():
    finance_username = os.getenv("FINANCE_USERNAME")
    user_exists = User.objects.filter(username=finance_username).exists()
    if user_exists:
        user = User.objects.get(finance_username)
        return user
    else:
        return None
        
def reward_user(user_reference, amount):
    message = {"success": True, "message": "User has been succesfully rewarded."}
    finance_username = os.getenv("FINANCE_USERNAME")
    finance_reference = os.getenv("FINANCE_REFERENCE")
    finance_user_exists = User.objects.filter(username=finance_username).exists()

    if finance_user_exists:
        finance_user = User.objects.get(username=finance_username)
        user = User.objects.get(reference=user_reference)
        if finance_user.balance > amount:
            SendPointsService.send_points(finance_user, user, amount, mode=SendPointsConstant.DIRECT)
            return message
        else:
            return {"success": False, "message": "Insufficient points in finance"}
    else:
        return {"success": False, "message": "No finance account registered"}
    

def bulk_reward(user_list, amount):
    #pass in a list containg references of users to reward
    message = {"success": True, "message": "User has been succesfully rewarded."}
    finance_username = os.getenv("FINANCE_USERNAME")
    finance_reference = os.getenv("FINANCE_REFERENCE")
    finance_user_exists = User.objects.filter(username=finance_username).exists()

    if finance_user_exists:
        finance_user = User.objects.get(username=finance_username)
        if finance_user.balance > amount:
            for users_reference in user_list:
                user = User.objects.get(reference = users_reference)
                status = SendPointsService.send_points(finance_user, user, amount, mode=SendPointsConstant.DIRECT)
                if status.get('success'):
                    return message
                return status
        else:
            return {"success": False, "message": "Insufficient points in finance"}
    else:
        return {"success": False, "message": "No finance account registered"}
    

def credit_finance(user_reference, amount):
    try:
        user = User.objects.get(reference=user_reference)
    except ObjectDoesNotExist:
        return {"success": False, "message": "user does not exist."}
    
    message = {"success": True, "message": "User has been succesfully rewarded."}
    finance_username = os.getenv("FINANCE_USERNAME")
    finance_reference = os.getenv("FINANCE_REFERENCE")
    finance_user_exists = User.objects.filter(username=finance_username).exists()

    if finance_user_exists:
        finance_user = User.objects.get(username=finance_username)
        if user.balance > amount:
            status = SendPointsService.send_points(user, finance_user, amount, mode=SendPointsConstant.DIRECT)
            if status.get('success'):
                    return message
            return status
        else:
            return {"success": False, "message": "Insufficient points in finance"}
    else:
        return {"success": False, "message": "No finance account registered"}
    
