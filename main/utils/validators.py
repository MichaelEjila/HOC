from django.core.exceptions import ValidationError
import re

class UserValidator():
    def validate_matric_number(value):
        # pattern = r'^EU-\d{4}$'
        # if not re.match(pattern, value):
        #     raise ValidationError('Invalid matric number format')
        pass
