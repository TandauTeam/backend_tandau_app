import re
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _


class CustomValidationException(Exception):
    def __init__(self, error_dict):
        self.error_dict = error_dict

class NumberValidator(object):
    def __init__(self, min_digits=8):
        self.min_digits = min_digits

    def validate(self, password, user=None):
        if len(password) < self.min_digits:
            error_message = _("Құпия сөзде кем дегенде %(min_digits)d санды болу керек, 0-9.") % {'min_digits': self.min_digits}
            raise CustomValidationException({'detail': error_message})


class UppercaseValidator(object):
    def validate(self, password, user=None):
        if not re.findall('[A-Z]', password):
            error_message = _("Құпия сөзде кем дегенде 1 үлкен таңба болу керек, A-Z керек.")
            raise CustomValidationException({'detail': error_message})

class LowercaseValidator(object):
    def validate(self, password, user=None):
        if not re.findall('[a-z]', password):
            error_message = _("Құпия сөзде кем дегенде 1 кіші таңба болу керек, a-z керек.")
            raise CustomValidationException({'detail': error_message})

class SymbolValidator(object):
    def validate(self, password, user=None):
        if not re.findall('[()[\]{}|\\`~!@#$%^&*_\-+=;:\'",<>./?]', password):
            error_message = _("Құпия сөзде кем дегенде 1 белгі: " +
                              "()[]{}|\`~!@#$%^&*_-+=;:'\",<>./? керек.")
            raise CustomValidationException({'detail': error_message})
        



class PhoneValidator(object):
    @staticmethod
    def validate(phone):
        if not re.match(r'^\+7\d{10}$', phone):
            error_message = _("Телефон нөмірі форматта енгізілуі керек: '+7XXXXXXXXXX', қайталаңыз.") 
            raise CustomValidationException({'detail': error_message})
        
