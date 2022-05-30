import uuid
import datetime

from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth import get_user_model
from django.urls import reverse


class TimeLog(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    user = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE,
        related_name='timelogs',
        related_query_name='timelog'
    )

    subject = models.ForeignKey('Subject', on_delete=models.CASCADE)
    tags = models.ManyToManyField('Tag', blank=True)
    description = models.CharField(max_length=500, blank=True)
    last_modified = models.DateTimeField(auto_now=True)
    date = models.DateField(
        default=datetime.date.today,
        validators=[MaxValueValidator(datetime.date.today)]
    )

    duration = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(1440)],
        help_text='Duration based on minutes'
    )

    class Meta:
        ordering = ['-last_modified']

    def get_absolute_url(self):
        return reverse('timing:timelog-detail', kwargs={'pk': self.pk})

    def __str__(self):
        return str(self.date) + ' ' + str(self.subject)


class Subject(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    description = models.CharField(max_length=500, blank=True)
    last_modified = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-last_modified']
        constraints = [
            models.UniqueConstraint(fields=('user', 'name'), name='unique_subject_name_for_each_user')
        ]

    def get_absolute_url(self):
        return reverse('timing:subject-detail', kwargs={'pk': self.pk})

    def __str__(self):
        return self.name


class Tag(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    last_modified = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-last_modified']
        constraints = [
            models.UniqueConstraint(fields=('user', 'name'), name='unique_tag_name_for_each_user')
        ]
    
    def get_absolute_url(self):
        return reverse('timing:tag-detail', kwargs={'pk': self.pk})

    def __str__(self):
        return self.name