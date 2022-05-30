from datetime import date

from django.test import TestCase
from django.contrib.auth import get_user_model

from timing.forms import DateForm, TimeLogForm, SubjectForm, TagForm
from timing.models import Subject, Tag, TimeLog


class DateFormTests(TestCase):
    """Test the DateForm"""
    def setUp(self):
        self.min_date = date(2021, 2, 22)
        self.max_date = date(2022, 2, 22)

    def test_dates_between_min_and_max_is_valid(self):
        """if start and end are between min and max dates then form should be valid"""
        form = DateForm(
            min_date=self.min_date,
            max_date=self.max_date,
            data={'start': date(2021, 4, 20), 'end': date(2022, 1, 22)}
        )
        self.assertTrue(form.is_valid())
        
    def test_dates_out_of_min_and_max_range_is_not_valid(self):
        """If start or end are out of min and max dates then form shoudn't be valid """
        form = DateForm(
            min_date=self.min_date,
            max_date=self.max_date,
            data={'start': date(2021, 1, 1), 'end': date(2022, 3, 22)}
        )
        self.assertFalse(form.is_valid())

    def test_mindate_greater_than_maxdate_is_not_valid(self):
        """If start date greater than end date then form shouldn't be valid"""
        form = DateForm(
            min_date=self.min_date,
            max_date=self.max_date,
            data={'start': date(2022, 1, 1), 'end': date(2021, 8, 22)}
        )
        self.assertFalse(form.is_valid())

    def test_form_is_not_valid_with_none_min_and_max_dates(self):
        """If min_date and max_date are None then form shouldn't be valid"""
        form = DateForm(
            min_date=None,
            max_date=None,
            data={'start': date(2021, 4, 20), 'end': date(2022, 1, 22)}
        )
        self.assertFalse(form.is_valid())


class TimeLogFormTests(TestCase):
    def setUp(self):
        self.user_1 = get_user_model().objects.create_user(
            username='user_1',
            password='testpass123',
            email='user_1@email.com')
        self.subject_1 = Subject.objects.create(user=self.user_1, name='subject 1')
        self.tag_1 = Tag.objects.create(user=self.user_1, name='tag 1')
        self.tag_2 = Tag.objects.create(user=self.user_1, name='tag 2')

        self.baduser = get_user_model().objects.create_user(
            username='baduser',
            password='testpass123',
            email='baduser@email.com')
        self.baduser_subject = Subject.objects.create(user=self.baduser, name='subject 1')
        self.baduser_tag = Tag.objects.create(user=self.baduser, name='tag 1')


    def test_form_with_correct_data_is_valid(self):
        form_data = {
            'subject': self.subject_1,
            'hours': 12,
            'minutes': 30,
            'date': date.today(),
            'tags': [self.tag_1, self.tag_2],
            'description': 'some test description'}
        form = TimeLogForm(data=form_data, registrant_user=self.user_1)
        self.assertTrue(form.is_valid())

    def test_fill_out_form_with_wrong_subject_is_not_valid(self):
        form_data = {
            'subject': self.baduser_subject,
            'hours': 12,
            'minutes': 30,
            'date': date.today(),
            'tags': [self.tag_1, self.tag_2],
            'description': 'some test description'}
        form = TimeLogForm(data=form_data, registrant_user=self.user_1)
        self.assertFalse(form.is_valid())
        self.assertIn(
            'Select a valid choice. That choice is not one of the available choices.',
            form.errors['subject']
        )

    def test_form_with_invalid_tag_is_not_valid(self):
        form_data = {
            'subject': self.subject_1,
            'hours': 12,
            'minutes': 30,
            'date': date.today(),
            'tags': [self.baduser_tag],
            'description': 'some test description'}
        form = TimeLogForm(data=form_data, registrant_user=self.user_1)
        self.assertFalse(form.is_valid())
        self.assertIn(
            f'Select a valid choice. {self.baduser_tag.pk} is not one of the available choices.',
            form.errors['tags']
        )

    def test_form_with_zero_hours_and_minutes_is_not_valid(self):
        form_data = {
            'subject': self.subject_1,
            'hours': 0,
            'minutes': 0,
            'date': date.today(),
            'tags': [self.tag_1, self.tag_2],
            'description': 'some test description'}
        form = TimeLogForm(data=form_data, registrant_user=self.user_1)
        self.assertFalse(form.is_valid())
        self.assertIn(
            'Both hour and minute fields can not be 0.',
            form.non_field_errors()
        )

    def test_duration_beyond_24_hours_is_not_valid(self):
        form_data = {
            'subject': self.subject_1,
            'hours': 24,
            'minutes': 30,
            'date': date.today(),
            'tags': [self.tag_1, self.tag_2],
            'description': 'some test description'}
        form = TimeLogForm(data=form_data, registrant_user=self.user_1)
        self.assertFalse(form.is_valid())
        self.assertIn('One day is 24 hours!', form.non_field_errors())

    def test_exceed_remind_duration_of_one_date_is_not_valid(self):
        # create and save one timelog
        today = date.today()
        TimeLog.objects.create(
            user=self.user_1,
            subject=self.subject_1,
            duration=12*60, # 12 hours
            date=today)
        # create form for today's date with 12 hours and 1 minutes duration
        form_data = {
            'subject': self.subject_1,
            'hours': 12,
            'minutes': 1,
            'date': today,
            'tags': [self.tag_1, self.tag_2],
            'description': 'some test description'}
        form = TimeLogForm(data=form_data, registrant_user=self.user_1)
        self.assertFalse(form.is_valid())
        self.assertIn(
            f"Your remaind duration for {today} is 12 hours and 0 minutes.",
            form.non_field_errors()
        )

    def test_exceed_duration_of_one_date_with_no_reminder_is_not_valid(self):
        # create and save one timelog
        today = date.today()
        TimeLog.objects.create(
            user=self.user_1,
            subject=self.subject_1,
            duration=24*60, # 24 hours
            date=today)
        # create form for today's date with 1 hours and 1 minutes duration
        form_data = {
            'subject': self.subject_1,
            'hours': 1,
            'minutes': 1,
            'date': today,
            'tags': [self.tag_1, self.tag_2],
            'description': 'some test description'}
        form = TimeLogForm(data=form_data, registrant_user=self.user_1)
        self.assertFalse(form.is_valid())
        self.assertIn(
            f'There is no time left for {today}',
            form.non_field_errors()
        )
        

class SubjectFormTests(TestCase):
    def setUp(self):
        self.test_user = get_user_model().objects.create_user(
            username='testuser',
            password='testpass123',
            email='testuser@email.com'
        )
        subject_1 = Subject.objects.create(user=self.test_user, name='subject 1')
    
    def test_form_with_correct_data_is_valid(self):
        form_data = {'name': 'subject 2', 'description': 'some description'}
        form = SubjectForm(data=form_data, user_subjects=self.test_user.subject_set.all())
        self.assertTrue(form.is_valid())
        
    def test_form_with_repeated_subject_name_is_not_valid(self):
        form_data = {'name': 'subject 1', 'description': 'some description'}
        form = SubjectForm(data=form_data, user_subjects=self.test_user.subject_set.all())
        self.assertFalse(form.is_valid())
        self.assertIn(
            'subject 1 already exists.',
            form.non_field_errors()
        )


class TagFormTests(TestCase):
    def setUp(self):
        self.test_user = get_user_model().objects.create_user(
            username='testuser',
            password='testpass123',
            email='testuser@email.com'
        )
        Tag.objects.create(user=self.test_user, name='tag 1')
    
    def test_form_with_uniuqe_name_is_valid(self):
        form = TagForm(data={'name': 'tag 2'}, user_tags=self.test_user.tag_set.all())
        self.assertTrue(form.is_valid())
        
    def test_form_with_repeated_tag_name_is_not_valid(self):
        form = TagForm(data={'name': 'tag 1'}, user_tags=self.test_user.tag_set.all())
        self.assertFalse(form.is_valid())
        self.assertIn(
            'tag 1 already exists.',
            form.non_field_errors()
        )