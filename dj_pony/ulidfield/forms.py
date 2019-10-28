from django.utils.translation import gettext_lazy as _
from django.forms import CharField, ValidationError
import ulid


class ULIDField(CharField):
    default_error_messages = {
        'invalid': _('Enter a valid ULID.'),
    }

    def prepare_value(self, value):
        if isinstance(value, ulid.ulid.ULID):
            return str(value)
        return value

    def to_python(self, value):
        value = super().to_python(value)
        if value in self.empty_values:
            return None
        if not isinstance(value, ulid.ulid.ULID):
            try:
                value = ulid.parse(value)
            except ValueError:
                raise ValidationError(self.error_messages['invalid'], code='invalid')
        return value
