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


class File(AutoReportModel):
    file_name = models.CharField(unique=True, max_length=50)
    key = models.CharField(unique=True, max_length=512)

    def __repr__(self):
        return self.file_name

    def __str__(self):
        return repr(self)