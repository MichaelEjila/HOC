from django.contrib.auth import get_user_model
from django.contrib.auth.backends import BaseBackend
from django.contrib.auth import login

class CustomAuthenticationBackend(BaseBackend):
    def authenticate(self, request, reference=None):
        User = get_user_model()
        try:
            user = User.objects.get(reference=reference)
        except User.DoesNotExist:
            return None
        
        # Perform additional checks or validations if needed
        login(request, user)
        
        return user
