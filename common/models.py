from django.db import models


class NameBaseModel(models.Model):
    NAME_MAX_LENGTH = 128
    name = models.CharField("Name", max_length=NAME_MAX_LENGTH, blank=True, default='')

    class Meta:
        abstract = True

    def __str__(self):
        return self.name
