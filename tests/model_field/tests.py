import json
import ulid
from time import sleep

from django.core import exceptions, serializers
from django.db import IntegrityError
from django.test import (
    SimpleTestCase, TestCase, TransactionTestCase, skipUnlessDBFeature,
)

from dj_pony.ulidfield.models import ULIDField
from tests.model_field.models import (
    NullableULIDModel,
    PrimaryKeyULIDModel,
    RelatedToULIDModel,
    ULIDGrandchild,
    ULIDModel,
    ULIDPrimaryKeyModel
)


class TestSaveLoad(TransactionTestCase):
    def test_ulid_instance(self):
        instance = ULIDModel.objects.create(field=ulid.new())
        loaded = ULIDModel.objects.get()
        self.assertEqual(loaded.field, instance.field)

    def test_str_instance_no_hyphens(self):
        ULIDModel.objects.create(field='550e8400e29b41d4a716446655440000')
        loaded = ULIDModel.objects.get()
        self.assertEqual(loaded.field, ulid.from_str('2N1T201RMV87AAE5J4CSAM8000'))

    def test_str_instance_hyphens(self):
        ULIDModel.objects.create(field='550e8400-e29b-41d4-a716-446655440000')
        loaded = ULIDModel.objects.get()
        self.assertEqual(loaded.field, ulid.from_str('2N1T201RMV87AAE5J4CSAM8000'))

    def test_null_handling(self):
        NullableULIDModel.objects.create(field=None)
        loaded = NullableULIDModel.objects.get()
        self.assertIsNone(loaded.field)

    def test_pk_validated(self):
        with self.assertRaisesMessage(exceptions.ValidationError, 'is not a valid ULID'):
            PrimaryKeyULIDModel.objects.get(pk={})

        with self.assertRaisesMessage(exceptions.ValidationError, 'is not a valid ULID'):
            PrimaryKeyULIDModel.objects.get(pk=[])

    def test_wrong_value(self):
        with self.assertRaisesMessage(exceptions.ValidationError, 'is not a valid ULID'):
            ULIDModel.objects.get(field='not-a-uuid')

        with self.assertRaisesMessage(exceptions.ValidationError, 'is not a valid ULID'):
            ULIDModel.objects.create(field='not-a-uuid')


class TestMethods(SimpleTestCase):

    def test_deconstruct(self):
        field = ULIDField()
        name, path, args, kwargs = field.deconstruct()
        self.assertEqual(kwargs, {})

    def test_to_python(self):
        self.assertIsNone(ULIDField().to_python(None))

    def test_to_python_int_values(self):
        self.assertEqual(
            ULIDField().to_python(0),
            ulid.parse('00000000-0000-0000-0000-000000000000')
        )
        # Works for integers less than 128 bits.
        self.assertEqual(
            ULIDField().to_python((2 ** 128) - 1),
            ulid.parse('ffffffff-ffff-ffff-ffff-ffffffffffff')
        )

    def test_to_python_int_too_large(self):
        # Fails for integers larger than 128 bits.
        with self.assertRaises(exceptions.ValidationError):
            ULIDField().to_python(2 ** 128)


class TestQuerying(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.objs = [
            NullableULIDModel.objects.create(field=ulid.new()),
            NullableULIDModel.objects.create(field='550e8400e29b41d4a716446655440000'),
            NullableULIDModel.objects.create(field=None),
        ]

    def test_exact(self):
        self.assertSequenceEqual(
            NullableULIDModel.objects.filter(field__exact='550e8400e29b41d4a716446655440000'),
            [self.objs[1]]
        )

    def test_isnull(self):
        self.assertSequenceEqual(
            NullableULIDModel.objects.filter(field__isnull=True),
            [self.objs[2]]
        )


class TestSerialization(SimpleTestCase):
    test_data = (
        '[{"fields": {"field": "2N1T201RMV87AAE5J4CSAM8000"}, '
        '"model": "model_field.ulidmodel", "pk": null}]'
    )
    nullable_test_data = (
        '[{"fields": {"field": null}, '
        '"model": "model_field.nullableulidmodel", "pk": null}]'
    )

    def test_dumping(self):
        instance = ULIDModel(field=ulid.parse('2N1T201RMV87AAE5J4CSAM8000'))
        data = serializers.serialize('json', [instance])
        self.assertEqual(json.loads(data), json.loads(self.test_data))

    def test_loading(self):
        instance = list(serializers.deserialize('json', self.test_data))[0].object
        self.assertEqual(instance.field, ulid.parse('2N1T201RMV87AAE5J4CSAM8000'))

    def test_nullable_loading(self):
        instance = list(serializers.deserialize('json', self.nullable_test_data))[0].object
        self.assertIsNone(instance.field)


class TestValidation(SimpleTestCase):
    def test_invalid_ulid(self):
        field = ULIDField()
        with self.assertRaises(exceptions.ValidationError) as cm:
            field.clean('550e8400', None)
        self.assertEqual(cm.exception.code, 'invalid')
        self.assertEqual(cm.exception.message % cm.exception.params, "'550e8400' is not a valid ULID.")

    def test_ulid_instance_ok(self):
        field = ULIDField()
        field.clean(ulid.new(), None)  # no error


class TestAsPrimaryKey(TestCase):
    def test_creation(self):
        PrimaryKeyULIDModel.objects.create()
        loaded = PrimaryKeyULIDModel.objects.get()
        self.assertIsInstance(loaded.pk, ulid.ulid.ULID)

    def test_ulid_pk_on_save(self):
        saved = PrimaryKeyULIDModel.objects.create(id=None)
        loaded = PrimaryKeyULIDModel.objects.get()
        self.assertIsNotNone(loaded.id, None)
        self.assertEqual(loaded.id, saved.id)

    def test_ulid_pk_on_bulk_create(self):
        u1 = PrimaryKeyULIDModel()
        u2 = PrimaryKeyULIDModel(id=None)
        PrimaryKeyULIDModel.objects.bulk_create([u1, u2])
        # The two objects were correctly created.
        u1_found = PrimaryKeyULIDModel.objects.filter(id=u1.id).exists()
        u2_found = PrimaryKeyULIDModel.objects.exclude(id=u1.id).exists()
        self.assertTrue(u1_found)
        self.assertTrue(u2_found)
        self.assertEqual(PrimaryKeyULIDModel.objects.count(), 2)

    def test_underlying_field(self):
        pk_model = PrimaryKeyULIDModel.objects.create()
        RelatedToULIDModel.objects.create(ulid_fk=pk_model)
        related = RelatedToULIDModel.objects.get()
        self.assertEqual(related.ulid_fk.pk, related.ulid_fk_id)

    def test_update_with_related_model_instance(self):
        # regression for #24611
        u1 = PrimaryKeyULIDModel.objects.create()
        u2 = PrimaryKeyULIDModel.objects.create()
        r = RelatedToULIDModel.objects.create(ulid_fk=u1)
        RelatedToULIDModel.objects.update(ulid_fk=u2)
        r.refresh_from_db()
        self.assertEqual(r.ulid_fk, u2)

    def test_update_with_related_model_id(self):
        u1 = PrimaryKeyULIDModel.objects.create()
        u2 = PrimaryKeyULIDModel.objects.create()
        r = RelatedToULIDModel.objects.create(ulid_fk=u1)
        RelatedToULIDModel.objects.update(ulid_fk=u2.pk)
        r.refresh_from_db()
        self.assertEqual(r.ulid_fk, u2)

    def test_two_level_foreign_keys(self):
        grandchild = ULIDGrandchild()
        # exercises ForeignKey.get_db_prep_value()
        grandchild.save()
        print(dir(grandchild))
        self.assertIsInstance(grandchild.ulidchild_ptr.id, ulid.ulid.ULID)
        grandchild.refresh_from_db()
        self.assertIsInstance(grandchild.ulidchild_ptr.id, ulid.ulid.ULID)

    def test_ulidprimarykeymodel_creation(self):
        ULIDPrimaryKeyModel.objects.create()
        loaded = ULIDPrimaryKeyModel.objects.get()
        self.assertIsInstance(loaded.pk, ulid.ulid.ULID)


class TestAsPrimaryKeyTransactionTests(TransactionTestCase):
    # Need a TransactionTestCase to avoid deferring FK constraint checking.
    available_apps = ['tests.model_field']

    @skipUnlessDBFeature('supports_foreign_keys')
    def test_unsaved_fk(self):
        u1 = PrimaryKeyULIDModel()
        with self.assertRaises(IntegrityError):
            RelatedToULIDModel.objects.create(ulid_fk=u1)


class PrimaryKeyOrderingTests(TransactionTestCase):
    def test_ordering(self):
        PrimaryKeyULIDModel.objects.all().delete()
        u1 = PrimaryKeyULIDModel.objects.create()
        sleep_delay = 2
        sleep(sleep_delay)
        u2 = PrimaryKeyULIDModel.objects.create()
        sleep(sleep_delay)
        u3 = PrimaryKeyULIDModel.objects.create()
        sleep(sleep_delay)
        u4 = PrimaryKeyULIDModel.objects.create()
        sleep(sleep_delay)
        u5 = PrimaryKeyULIDModel.objects.create()
        first = PrimaryKeyULIDModel.objects.first()
        last = PrimaryKeyULIDModel.objects.last()
        self.assertEqual(u1, first)
        self.assertEqual(u5, last)
