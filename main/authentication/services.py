from django.contrib.auth import authenticate, get_user_model
User = get_user_model()

class UserAuthenticationService():

    def authenticate_user(hash):
        try:
            user = User.objects.get(reference=hash)
            return authenticate(request=None, matric_number=user.matric_number, password=None)
        except User.DoesNotExist:
            return None
        
