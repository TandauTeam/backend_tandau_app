import re
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _ # Changed to gettext_lazy

# ---
# CustomValidationException is not needed if you raise Django's ValidationError
# If you still need a custom exception for other parts of your app, keep it,
# but for password validators, ValidationError is preferred.
# class CustomValidationException(Exception):
#     def __init__(self, error_dict):
#         self.error_dict = error_dict
# ---
# tandau_app/validators.py

# ... (other imports)

class CustomValidationException(Exception):
    def __init__(self, error_dict):
        self.error_dict = error_dict

# ... (your validators)
class NumberValidator(object):
    def __init__(self, min_digits=1): # Changed default to 1, as per your settings
        self.min_digits = min_digits

    def validate(self, password, user=None):
        # Check for at least one digit and total length
        if not re.search(r'\d', password) or len(password) < self.min_digits:
            error_message = _("Құпия сөзде кем дегенде %(min_digits)d санды болу керек, 0-9.") % {'min_digits': self.min_digits}
            raise ValidationError({'detail': error_message}) # Raise Django's ValidationError

    def get_help_text(self):
        return _("Your password must contain at least %(min_digits)d digit(s)." % {'min_digits': self.min_digits})


class UppercaseValidator(object):
    def validate(self, password, user=None):
        if not re.findall(r'[A-Z]', password): # Using raw string
            error_message = _("Құпия сөзде кем дегенде 1 үлкен таңба болу керек, A-Z керек.")
            raise ValidationError({'detail': error_message}) # Raise Django's ValidationError

    def get_help_text(self):
        return _("Your password must contain at least 1 uppercase letter, A-Z.")


class LowercaseValidator(object):
    def validate(self, password, user=None):
        if not re.findall(r'[a-z]', password): # Using raw string
            error_message = _("Құпия сөзде кем дегенде 1 кіші таңба болу керек, a-z керек.")
            raise ValidationError({'detail': error_message}) # Raise Django's ValidationError

    def get_help_text(self):
        return _("Your password must contain at least 1 lowercase letter, a-z.")


class SymbolValidator(object):
    def validate(self, password, user=None):
        # Using a raw string (r'...') for the regex pattern.
        # Inside a character class, `]` needs escaping as `\]`.
        # `-` needs escaping as `\-` if not at the start/end of the class.
        # Backtick ` can be included directly.
        if not re.findall(r'[()[\]{}|`~!@#$%^&*_\-+=;:\'",<>./?]', password):
            error_message = _("Құпия сөзде кем дегенде 1 белгі: "
                              "()[]{}|`~!@#$%^&*_-+=;:'\",<>./? керек.")
            raise ValidationError({'detail': error_message}) # Raise Django's ValidationError

    def get_help_text(self):
        return _("Your password must contain at least 1 symbol.")


class PhoneValidator(object):
    @staticmethod
    def validate(phone):
        if not re.match(r'^\+7\d{10}$', phone): # Using raw string
            error_message = _("Телефон нөмірі форматта енгізілуі керек: '+7XXXXXXXXXX', қайталаңыз.")
            raise ValidationError({'detail': error_message}) # Raise Django's ValidationError
