# noinspection PyPackageRequirements
import ulid

from django.db import models
from dj_pony.ulidfield.models import ULIDField
from dj_pony.ulidfield.models import ULIDPrimaryKey


class ULIDModel(models.Model):
    field = ULIDField(default=None, null=False)


class NullableULIDModel(models.Model):
    field = ULIDField(blank=True, null=True)


class PrimaryKeyULIDModel(models.Model):
    id = ULIDField(primary_key=True, default=ulid.new)


class RelatedToULIDModel(models.Model):
    ulid_fk = models.ForeignKey('PrimaryKeyULIDModel', models.CASCADE)


class ULIDChild(PrimaryKeyULIDModel):
    pass


class ULIDGrandchild(ULIDChild):
    pass


class ULIDPrimaryKeyModel(models.Model):
    id = ULIDPrimaryKey()
