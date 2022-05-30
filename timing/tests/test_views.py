import datetime
import json
from time import sleep

from django.test import TestCase
from django.urls import reverse, resolve
from django.contrib.auth import get_user_model

import timing
from timing.models import TimeLog, Subject, Tag



class IndexViewTests(TestCase):
    """Test the index view"""
    def setUp(self):
        get_user_model().objects.create_user(
            email='testuser@gmail.com',
            username='testuser',
            password='testpass123'
        )
        self.url = reverse('timing:index')
        self.response = self.client.get(self.url)

    def test_index_page_url_resolves_index_view(self):
        """ index url should resolves the index_view """
        view = resolve(self.url)
        self.assertEqual(
            view.func,
            timing.views.index
        )

    def test_index_page_status_code(self):
        """index page status code must be 200"""
        self.assertEqual(self.response.status_code, 200)

    def test_get_index_page_with_logged_in_user(self):
        """if user is already logged in, and then user should redirect to the home page"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(self.url, follow=True)
        self.assertEqual(response.resolver_match.func, timing.views.home)
        
    def test_index_page_template(self):
        """index page template is index.html"""
        self.assertTemplateUsed(self.response, 'index.html')


class HomeViewTests(TestCase):
    """Test the Home page view"""
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email='testuser@gmail.com',
            username='testuser',
            password='testpass123'
        )
        # login the user
        self.client.login(username='testuser', password='testpass123')
        self.url = reverse('timing:home')

    def test_home_page_url_resolves_home_view(self):
        view = resolve(self.url)
        self.assertEqual(
            view.func,
            timing.views.home
        )

    def test_home_page_status_code(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_home_page_status_code_without_login(self):
        self.client.logout()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)

    def test_home_page_template(self):
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, 'timing/home.html')
    
    def test_charts_json_data(self):
        # creating subjects
        subject_1 = Subject.objects.create(user=self.user, name='subject_1')
        subject_2 = Subject.objects.create(user=self.user, name='subject_2')
        # creating tags
        tag_1 = Tag.objects.create(user=self.user, name='tag_1')
        tag_2 = Tag.objects.create(user=self.user, name='tag_2')
        # creating timelogs
        today = datetime.date.today()
        yesterday = today - datetime.timedelta(days=1)
        timelog_1 = TimeLog.objects.create(
            user=self.user,
            subject=subject_1,
            date=today,
            duration=120
        )
        timelog_1.tags.add(tag_1, tag_2)
        sleep(0.01)
        timelog_2 = TimeLog.objects.create(
            user=self.user,
            subject=subject_2,
            date=today,
            duration=60
        )
        sleep(0.01)
        timelog_3 = TimeLog.objects.create(
            user=self.user,
            subject=subject_1,
            date=yesterday,
            duration=240
        )
        timelog_3.tags.add(tag_2)
        sleep(0.01)
        timelog_4 = TimeLog.objects.create(
            user=self.user,
            subject=subject_2,
            date=yesterday,
            duration=120
        )
        timelog_4.tags.add(tag_1)

        # date based chart datasets
        date_based_chart_labels = [yesterday.isoformat(), today.isoformat()]
        date_based_chart_datasets = [
            {'label': subject_1.name, 'data': [(timelog_3.duration // 60), (timelog_1.duration // 60)]},
            {'label': subject_2.name, 'data': [(timelog_4.duration // 60), (timelog_2.duration // 60)]}
        ]
        # subject based chart datasets
        subject_based_chart_labels = [subject_1.name, subject_2.name]
        subject_based_chart_dataset_data = [
            ((timelog_1.duration + timelog_3.duration) // 60),
            ((timelog_2.duration + timelog_4.duration) // 60)
        ]
        # tag based chart datasets
        tag_based_chart_labels = [tag_2.name, tag_1.name]
        tag_based_chart_dataset_data = [
            ((timelog_1.duration + timelog_3.duration) // 60),
            ((timelog_1.duration + timelog_4.duration) // 60)
        ]
        # get json charts data from home page and convert it to python objects
        response = self.client.get(self.url, data={'start': yesterday.isoformat(), 'end': today.isoformat()})
        date_based_chart_data = response.context['date_based_chart_data']
        subject_based_chart_data = response.context['subject_based_chart_data']
        tag_based_chart_data = response.context['tag_based_chart_data']

        # date based chart data asserts
        self.assertEqual(date_based_chart_data['labels'], date_based_chart_labels)
        # test firs dataset
        self.assertEqual(
            date_based_chart_data['datasets'][0]['data'],
            date_based_chart_datasets[0]['data']
        )
        # test seccond dataset
        self.assertEqual(
            date_based_chart_data['datasets'][1]['data'],
            date_based_chart_datasets[1]['data']
        )
        # subject based chart data asserts
        self.assertEqual(subject_based_chart_data['labels'], subject_based_chart_labels)
        self.assertEqual(
            subject_based_chart_data['datasets'][0]['data'],
            subject_based_chart_dataset_data
        )
        # tag based chart data asserts
        self.assertEqual(tag_based_chart_data['labels'], tag_based_chart_labels)
        self.assertEqual(
            tag_based_chart_data['datasets'][0]['data'],
            tag_based_chart_dataset_data
        )

        # test the home page recent timelogs
        recent_timelogs = [timelog_4, timelog_3, timelog_2, timelog_1]
        context_recent_timelogs = response.context['timelogs']
        self.assertEqual(
            [(t.subject.name, t.duration, t.date) for t in recent_timelogs],
            [(t.subject.name, t.duration, t.date) for t in context_recent_timelogs]
        )


class TimeLogDetailViewTests(TestCase):
    def setUp(self):
        user = get_user_model().objects.create_user(username='test', password='testpass123')
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
        self.url = reverse('timing:timelog-detail', kwargs={'pk': self.timelog.pk})
        self.client.login(username='test', password='testpass123')
        self.response = self.client.get(self.url)

    def test_timelog_detail_url_resolves_timelog_detail_view(self):
        view = resolve(self.url)
        self.assertEqual(
            view.func,
            timing.views.timelog_detail
        )

    def test_timelog_detail_status_code(self):
        self.assertEqual(self.response.status_code, 200)

    def test_timelog_detail_context(self):
        self.assertEqual(self.response.context['timelog'], self.timelog)

    def test_timelog_detail_template(self):
        self.assertTemplateUsed(self.response, 'timing/timelog_detail.html')


class SubjectsViewTests(TestCase):
    def setUp(self):
        self.testuser = get_user_model().objects.create_user(
            username='testuser',
            password='testpass123',
            email='testuser@email.com'
        )

        self.page_url = reverse('timing:subjects')
        self.client.login(username='testuser', password='testpass123')

    def test_status_code(self):
        response = self.client.get(self.page_url)
        self.assertEqual(response.status_code, 200)
    
    def test_context_contains_subject(self):
        subject = Subject.objects.create(user=self.testuser, name='subject')
        response = self.client.get(self.page_url)
        self.assertContains(response, subject.name)
        
    def test_add_valid_subject(self):
        subject_data = {
            'name': 'test subject',
            'description': 'some description for test subject'
        }
        response = self.client.post(self.page_url, subject_data, follow=True)
        self.assertContains(response, "Subject &quot;test subject&quot; successfully added!")


class SubjectDetailViewTests(TestCase):
    def setUp(self):
        user = get_user_model().objects.create_user(
            username='testuser',
            password='testpass123',
            email='testuser@email.com'
        )
        self.subject = Subject.objects.create(user=user, name='test subject')
        self.url = reverse('timing:subject-detail', kwargs={'pk': self.subject.pk})
        self.client.login(username='testuser', password='testpass123')

    def test_subject_detail_url_resolves_subject_detail_view(self):
        view = resolve(self.url)
        self.assertEqual(
            timing.views.subject_detail,
            view.func
        )

    def test_subject_detail_status_code(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_subject_detail_template(self):
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, 'timing/subject_detail.html')
    
    def test_update_subject_name(self):
        subject_data = {'name': 'updated name', 'descripion': 'some description'}
        response = self.client.post(self.url, subject_data, follow=True)
        self.assertContains(response, 'updated name')
        

class SubjectDeleteViewTests(TestCase):
    def setUp(self):
        user = get_user_model().objects.create_user(
            username='testuser',
            password='testpass123',
            email='testuser@email.com'
        )
        self.client.login(username='testuser', password='testpass123')
        subject = Subject.objects.create(user=user, name='test subject')
        self.page_url = reverse('timing:subject-delete', kwargs={'pk': subject.pk})
        
    def test_valid_subject_status_code(self):
        response = self.client.get(self.page_url)
        self.assertEqual(response.status_code, 200)
        
    def test_delete_subject(self):
        response = self.client.post(self.page_url, follow=True)
        self.assertContains(response, "Subject &quot;test subject&quot; successfully deleted!")


class TagsViewTests(TestCase):
    def setUp(self):
        self.testuser = get_user_model().objects.create_user(
            username='testuser',
            password='testpass123',
            email='testuser@email.com'
        )

        self.page_url = reverse('timing:tags')
        self.client.login(username='testuser', password='testpass123')

    def test_status_code(self):
        response = self.client.get(self.page_url)
        self.assertEqual(response.status_code, 200)
    
    def test_context_contains_tag(self):
        tag = Tag.objects.create(user=self.testuser, name='tag')
        response = self.client.get(self.page_url)
        self.assertContains(response, tag.name)
        
    def test_add_valid_tag(self):
        response = self.client.post(self.page_url, {'name': 'test tag'}, follow=True)
        self.assertContains(response, "Tag &quot;test tag&quot; successfully added!")


class TagDetailViewTests(TestCase):
    def setUp(self):
        user = get_user_model().objects.create_user(
            username='test',
            password='testpass123',
            email='testuser@email.com'
        )
        self.client.login(username='test', password='testpass123')
        self.tag = Tag.objects.create(user=user, name='test tag')
        self.url = reverse('timing:tag-detail', kwargs={'pk': self.tag.pk})
        self.response = self.client.get(self.url)

    def test_tag_detail_url_resolves_tag_detail_view(self):
        view = resolve(self.url)
        self.assertEqual(
            timing.views.tag_detail,
            view.func
        )

    def test_tag_detail_status_code(self):
        self.assertEqual(self.response.status_code, 200)

    def test_tag_detail_template(self):
        self.assertTemplateUsed(self.response, 'timing/tag_detail.html')

    def test_update_tag_name(self):
        response = self.client.post(self.url, {'name': 'updated name'}, follow=True)
        self.assertContains(response, 'updated name')


class TagDeleteViewTests(TestCase):
    def setUp(self):
        user = get_user_model().objects.create_user(
            username='testuser',
            password='testpass123',
            email='testuser@email.com'
        )
        self.client.login(username='testuser', password='testpass123')
        tag = Tag.objects.create(user=user, name='test tag')
        self.page_url = reverse('timing:tag-delete', kwargs={'pk': tag.pk})
        
    def test_valid_tag_status_code(self):
        response = self.client.get(self.page_url)
        self.assertEqual(response.status_code, 200)
        
    def test_delete_tag(self):
        response = self.client.post(self.page_url, follow=True)
        self.assertContains(response, "Tag &quot;test tag&quot; successfully deleted!")

    
class TimelogsViewTests(TestCase):
    def setUp(self):
        user_1 = get_user_model().objects.create_user(username='user_1', password='testpass123')
        self.subject_1 = Subject.objects.create(user=user_1, name='subject 1')
        self.tag_1 = Tag.objects.create(user=user_1, name='tag 1')
        self.tag_2 = Tag.objects.create(user=user_1, name='tag 2')

        self.timelogs_page_url = reverse('timing:timelogs')
        self.client.login(username='user_1', password='testpass123')

    def test_timelogs_page_status_code(self):
        response = self.client.get(self.timelogs_page_url)
        self.assertEqual(response.status_code, 200)

    def test_add_new_valid_timelog_record(self):
        post_data = {
            'subject': self.subject_1.pk,
            'hours': 8,
            'minutes': 30,
            'date': datetime.date.today().isoformat(),
            'tags': [self.tag_1.pk, self.tag_2.pk],
            'description': 'some dummy description',
        }
        response = self.client.post(self.timelogs_page_url, data=post_data, follow=True)
        self.assertContains(response, 'Record successfully added!')
        self.assertContains(response, post_data['description'])

    def test_add_timelog_record_with_invalid_subject(self):
        post_data = {
            'subject': 'invalid_subject',
            'hours': 8,
            'minutes': 30,
            'date': datetime.date.today().isoformat(),
            'tags': [self.tag_1.pk, self.tag_2.pk],
            'description': 'some dummy description',
        }
        response = self.client.post(self.timelogs_page_url, data=post_data, follow=True)
        self.assertContains(response, '“invalid_subject” is not a valid UUID')


class TimelogDeleteTests(TestCase):

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email='testuser@gmail.com',
            username='testuser',
            password='testpass123'
        )
        # create timelog
        subject_1 = Subject.objects.create(user=self.user, name='subject_1')
        tag_1 = Tag.objects.create(user=self.user, name='tag_1')
        tag_2 = Tag.objects.create(user=self.user, name='tag_2')
        self.timelog = TimeLog.objects.create(
            user=self.user,
            subject=subject_1,
            date=datetime.date.today(),
            duration=120
        )
        self.timelog.tags.add(tag_1, tag_2)
        
        self.client.login(username='testuser', password='testpass123')
        self.url = reverse('timing:timelog-delete', kwargs={'pk': self.timelog.pk})

    def test_timelog_delete_page_status_code(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_delete_timelog_record(self):
        response = self.client.post(self.url, follow=True)
        self.assertContains(response, 'Record successfully deleted!')
