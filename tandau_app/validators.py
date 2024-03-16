import re
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _

class NumberValidator(object):
    def __init__(self, min_digits=5):
        self.min_digits = min_digits

    def validate(self, password, user=None):
        if not len(password) >= self.min_digits:
            error_message = _("Құпия сөзде кем дегенде %(min_digits)d санды болу керек, 0-9.") % {'min_digits': self.min_digits}
            raise ValidationError({"error": error_message}, code='password_no_number')

class UppercaseValidator(object):
    def validate(self, password, user=None):
        if not re.findall('[A-Z]', password):
            error_message = _("Құпия сөзде кем дегенде 1 үлкен таңба болу керек, A-Z керек.")
            raise ValidationError({"error": error_message}, code='password_no_upper')

class LowercaseValidator(object):
    def validate(self, password, user=None):
        if not re.findall('[a-z]', password):
            error_message = _("Құпия сөзде кем дегенде 1 кіші таңба болу керек, a-z керек.")
            raise ValidationError({"error": error_message}, code='password_no_lower')

class SymbolValidator(object):
    def validate(self, password, user=None):
        if not re.findall('[()[\]{}|\\`~!@#$%^&*_\-+=;:\'",<>./?]', password):
            error_message = _("Құпия сөзде кем дегенде 1 белгі: " +
                              "()[]{}|\`~!@#$%^&*_-+=;:'\",<>./? керек.")
            raise ValidationError({"error": error_message}, code='password_no_symbol')
