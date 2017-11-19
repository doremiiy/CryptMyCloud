from django.contrib.auth.models import User
from django.core.validators import MinLengthValidator
from django.db import models
from django.utils import timezone


class AutoReportModel(models.Model):
    created_at = models.DateTimeField(editable=False)
    updated_at = models.DateTimeField(blank=True)

    def save(self, *args, **kwargs):
        self._prepopulate_fields()
        super(AutoReportModel, self).save(**kwargs)

    def _prepopulate_fields(self):
        now = timezone.now()
        if not self.created_at:
            self.created_at = now
        self.updated_at = now

    class Meta:
        abstract = True


class Key(AutoReportModel):
    key = models.CharField(max_length=32, validators=[MinLengthValidator(32)])

    def __repr__(self):
        return self.key

    def __str__(self):
        return repr(self)


class File(AutoReportModel):
    file_name = models.CharField(unique=True, max_length=50)

    key = models.ForeignKey(Key, null=True)
    # owner = models.ForeignKey(User, on_delete=models.CASCADE)

    def __repr__(self):
        return self.file_name

    def __str__(self):
        return repr(self)
