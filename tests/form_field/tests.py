# noinspection PyPackageRequirements
import ulid

from django.test import SimpleTestCase
from django.forms import ValidationError
from dj_pony.ulidfield.forms import ULIDField


class ULIDFieldTest(SimpleTestCase):
    def test_none(self):
        field = ULIDField(required=False)
        value = field.clean(None)
        self.assertEqual(value, None)

    def test_ulidfield_1(self):
        field = ULIDField()
        value = field.clean('550e8400e29b41d4a716446655440000')
        self.assertEqual(value, ulid.parse('550e8400e29b41d4a716446655440000'))

    def test_clean_value_with_dashes(self):
        field = ULIDField()
        value = field.clean('550e8400-e29b-41d4-a716-446655440000')
        self.assertEqual(value, ulid.parse('550e8400e29b41d4a716446655440000'))

    def test_ulidfield_2(self):
        field = ULIDField(required=False)
        value = field.clean('')
        self.assertIsNone(value)

    def test_ulidfield_3(self):
        field = ULIDField()
        with self.assertRaisesMessage(ValidationError, 'Enter a valid ULID.'):
            field.clean('550e8400')

    def test_ulidfield_4(self):
        field = ULIDField()
        value = field.prepare_value(ulid.parse('2N1T201RMV87AAE5J4CSAM8000'))
        self.assertEqual(value, '2N1T201RMV87AAE5J4CSAM8000')
