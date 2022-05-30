from django.contrib import admin

from .models import TimeLog, Subject, Tag



admin.site.register(TimeLog)
admin.site.register(Tag)
admin.site.register(Subject)
