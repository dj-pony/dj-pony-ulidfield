"""
"""
from django.db.models.fields import Field
from django.utils.translation import gettext_lazy as _
from django.core import exceptions
from django.db.utils import NotSupportedError
import ulid
import copyreg
from dj_pony.ulidfield import forms


def pickle_ulid(original_ulid: ulid.ULID) -> tuple:
    """Allows copy, deepcopy and pickle to work on ULID objects."""
    return ulid.ULID, (original_ulid.bytes,)


# Register our pickle function!
copyreg.pickle(ulid.ULID, pickle_ulid)


class ULIDField(Field):
    default_error_messages = {
        'invalid': _("'%(value)s' is not a valid ULID."),
    }
    description = _('Universally Unique Lexicographically Sortable Identifier')
    empty_strings_allowed = False

    def __init__(self, verbose_name=None, **kwargs):
        kwargs['max_length'] = 32
        super().__init__(verbose_name, **kwargs)

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        if 'max_length' in kwargs:
            del kwargs['max_length']
        return name, path, args, kwargs

    def db_type(self, connection):
        # I've just copied the same column types Django uses for UUIDs.
        if connection.settings_dict['ENGINE'] == 'django.db.backends.sqlite3':
            return 'char(32)'  # A 16 byte BLOB might be better...
        elif connection.settings_dict['ENGINE'] == 'django.db.backends.postgresql':
            return 'uuid'
        elif connection.settings_dict['ENGINE'] == 'django.db.backends.mysql':
            return 'char(32)'
        elif connection.settings_dict['ENGINE'] == 'django.db.backends.oracle':
            return 'VARCHAR2(32)'
        else:
            raise NotSupportedError(
                "You are trying to use a backend that is not currently supported by this field."
            )

    def get_db_prep_value(self, value, connection, prepared=False):
        if value is None:
            return None
        if not isinstance(value, ulid.ulid.ULID):
            value = self.to_python(value)
        if connection.features.has_native_uuid_field:
            return value.uuid
        return value.str

    def get_prep_value(self, value):
        value = super().get_prep_value(value)
        if value is None:
            return None
        return self.to_python(value)

    def to_python(self, value):
        if value is not None and not isinstance(value, ulid.ulid.ULID):
            try:
                return ulid.parse(value)
            except (AttributeError, ValueError):
                raise exceptions.ValidationError(
                    self.error_messages['invalid'],
                    code='invalid',
                    params={'value': value},
                )
        return value

    def from_db_value(self, value, expression, connection):
        if value is None:
            return value
        return ulid.parse(value)

    def formfield(self, **kwargs):
        return super().formfield(**{
            'form_class': forms.ULIDFormField,
            **kwargs,
        })
