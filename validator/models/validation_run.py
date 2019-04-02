from os import path
from re import sub as regex_sub
from shutil import rmtree
import uuid

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models.signals import post_delete
from django.dispatch.dispatcher import receiver


class ValidationRun(models.Model):

    ## scaling methods
    MIN_MAX = 'min_max'
    LINREG = 'linreg'
    MEAN_STD = 'mean_std'
    LIN_CDF_MATCH = 'lin_cdf_match'
    CDF_MATCH = 'cdf_match'

    SCALING_METHODS = (
        (MIN_MAX, 'Min/Max'),
        (LINREG, 'Linear regression'),
        (MEAN_STD, 'Mean/standard deviation'),
#         (LIN_CDF_MATCH, 'CDF matching with linear interpolation'),
#         (CDF_MATCH, 'CDF matching with 5-th order spline fitting'),
        )

    ## fields

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name_tag = models.CharField(max_length=80, blank=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    start_time = models.DateTimeField('started')
    end_time = models.DateTimeField('finished', null=True)
    total_points = models.IntegerField(default=0)
    error_points = models.IntegerField(default=0)
    ok_points = models.IntegerField(default=0)
    progress = models.IntegerField(default=0)
    
    scaling_method = models.CharField(max_length=20, choices=SCALING_METHODS, default=MEAN_STD)
    interval_from = models.DateTimeField(null=True)
    interval_to = models.DateTimeField(null=True)

    output_file = models.FileField(null=True)
    
    # many-to-one relationships coming from other models:
    # dataset_configuration from DatasetConfiguration



    # many-to-one relationships coming from other models:
    # celery_tasks from CeleryTask

    def clean(self):
        if self.interval_from is None and self.interval_to is not None:
            raise ValidationError({'interval_from': 'What has an end must have a beginning.',})
        if self.interval_from is not None and self.interval_to is None:
            raise ValidationError({'interval_to': 'What has a beginning must have an end.',})
        if self.interval_from is not None and self.interval_to is not None and self.interval_from > self.interval_to:
            raise ValidationError({'interval_from': 'From must be before To',
                                   'interval_to': 'From must be before To',})

    def __str__(self):
        return "id: {}, user: {}, start: {} )".format(self.id, self.user, self.start_time)

    def output_dir_url(self):
        if bool(self.output_file) is False:
            return None
        url = regex_sub('[^/]+$', '', self.output_file.url)
        return url


# delete model output directory on disk when model is deleted
@receiver(post_delete, sender=ValidationRun)
def auto_delete_file_on_delete(sender, instance, **kwargs):
    if instance.output_file:
        rundir = path.dirname(instance.output_file.path)
        if path.isdir(rundir):
            rmtree(rundir)
