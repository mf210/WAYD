# Generated by Django 4.0.3 on 2022-05-07 12:05

import datetime
from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Subject',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=200)),
                ('description', models.CharField(blank=True, max_length=500)),
                ('last_modified', models.DateTimeField(auto_now=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-last_modified'],
            },
        ),
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=200)),
                ('last_modified', models.DateTimeField(auto_now=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-last_modified'],
            },
        ),
        migrations.CreateModel(
            name='TimeLog',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('description', models.CharField(blank=True, max_length=500)),
                ('last_modified', models.DateTimeField(auto_now=True)),
                ('date', models.DateField(default=datetime.date.today, validators=[django.core.validators.MaxValueValidator(datetime.date.today)])),
                ('duration', models.PositiveSmallIntegerField(help_text='Duration based on minutes', validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(1440)])),
                ('subject', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='timing.subject')),
                ('tags', models.ManyToManyField(blank=True, to='timing.tag')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='timelogs', related_query_name='timelog', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-last_modified'],
            },
        ),
        migrations.AddConstraint(
            model_name='tag',
            constraint=models.UniqueConstraint(fields=('user', 'name'), name='unique_tag_name_for_each_user'),
        ),
        migrations.AddConstraint(
            model_name='subject',
            constraint=models.UniqueConstraint(fields=('user', 'name'), name='unique_subject_name_for_each_user'),
        ),
    ]
