import datetime

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from timing.models import TimeLog, Subject, Tag



class TimeLogModelTests(TestCase):
    def setUp(self):
        user = get_user_model().objects.create(username='test', password='testpass123')
        subject = Subject.objects.create(user=user, name='test subject')
        tag_1 = Tag.objects.create(user=user, name='test tag 1')
        tag_2 = Tag.objects.create(user=user, name='test tag 2')
        self.timelog = TimeLog.objects.create(
            user=user,
            subject=subject,
            date=datetime.date.today(),
            duration=120
        )
        self.timelog.tags.add(tag_1, tag_2)
    
    def test_get_absolute_url_method(self):
        timelog_url = reverse('timing:timelog-detail', kwargs={'pk': self.timelog.pk})
        self.assertEqual(self.timelog.get_absolute_url(), timelog_url)
        self.assertEqual(str(self.timelog), f'{self.timelog.date} {self.timelog.subject}')


class SubjectModelTests(TestCase):
    def setUp(self):
        user = get_user_model().objects.create(username='test', password='testpass123')
        self.subject = Subject.objects.create(user=user, name='test subject')

    def test_get_absolute_url_method(self):
        subject_url = reverse('timing:subject-detail', kwargs={'pk': self.subject.pk})
        self.assertEqual(self.subject.get_absolute_url(), subject_url)
        self.assertEqual(str(self.subject), self.subject.name)


class TagModelTests(TestCase):
    def setUp(self):
        user = get_user_model().objects.create(username='test', password='testpass123')
        self.tag = Tag.objects.create(user=user, name='test tag')

    def test_get_absolute_url_method(self):
        tag_url = reverse('timing:tag-detail', kwargs={'pk': self.tag.pk})
        self.assertEqual(self.tag.get_absolute_url(), tag_url)
        self.assertEqual(str(self.tag), self.tag.name)
