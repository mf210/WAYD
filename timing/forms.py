import datetime

from django import forms
from django.core.exceptions import ValidationError

from .models import TimeLog, Subject, Tag


class DateForm(forms.Form):
    def __init__(self, *args, **kwargs):
        self.min_date = kwargs.pop('min_date')
        self.max_date = kwargs.pop('max_date')
        # if user has no record (min_date and max_date is None) then disable the date inputs else set the min and max attrs
        if self.min_date and self.max_date:
            self.base_fields['start'].widget.attrs['min'] = self.min_date.isoformat()
            self.base_fields['start'].widget.attrs['max'] = self.max_date.isoformat()
            self.base_fields['end'].widget.attrs['min'] = self.min_date.isoformat()
            self.base_fields['end'].widget.attrs['max'] = self.max_date.isoformat()
        else:
            self.base_fields['start'].widget.attrs['disabled'] = True
            self.base_fields['end'].widget.attrs['disabled'] = True

        super().__init__(*args, **kwargs)

    start = forms.DateField(label='From')
    end = forms.DateField(label='To')

    def clean(self):
        # if min_date or max_date is none, it means that user has no record yet
        if self.min_date is None:
            raise ValidationError("You don't have any record!")

        cleaned_data = super().clean()
        start = cleaned_data.get('start')
        end = cleaned_data.get('end')
        if start and end:
            if start > end:
                raise ValidationError('Your selected start date is greater then selected end date')
            if not (self.min_date <= start <= self.max_date and self.min_date <= end <= self.max_date):
                raise ValidationError(f'Your records date are between {self.min_date} and {self.max_date}')
        return cleaned_data


class TimeLogForm(forms.ModelForm):
    hours = forms.IntegerField(min_value=0, max_value=24)
    minutes = forms.IntegerField(min_value=0, max_value=59)

    def __init__(self, *args, **kwargs):
        self.registrant_user = kwargs.pop('registrant_user', None)
        super().__init__(*args, **kwargs)
        # add registrant user's subjects and tags to the corresponding field choices
        self.fields['subject'].queryset = self.registrant_user.subject_set.all()
        self.fields['tags'].queryset = self.registrant_user.tag_set.all()
        # add html attribute to the widget of fields
        self.fields['subject'].widget.attrs['class'] = 'form-select'
        self.fields['tags'].widget.attrs['class'] = 'form-select'
        self.fields['tags'].widget.attrs['size'] = '3'
        self.fields['date'].widget.attrs['class'] = 'form-control'
        self.fields['hours'].widget.attrs['class'] = 'form-control'
        self.fields['minutes'].widget.attrs['class'] = 'form-control'
        self.fields['description'].widget.attrs['class'] = 'form-control'

    class Meta:
        model = TimeLog
        exclude = ['user', 'duration']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'max': datetime.date.today}),
        }

    def clean(self):
        clean_data = super().clean()
        hours = clean_data.get('hours')
        minutes = clean_data.get('minutes')
        date = clean_data.get('date')

        # calculate and check if the duration is valid
        if hours is not None and minutes is not None and date:
            # calculate duration minutes based on hours and minutes
            duration = (hours * 60) + minutes
            if duration == 0:
                raise ValidationError("Both hour and minute fields can not be 0.")
            
            if duration > 1440:
                raise ValidationError("One day is 24 hours!")

            # check the particular date's durations doesn't exceed 24 hours
            previous_durations_total = 0
            for timelog in self.registrant_user.timelogs.filter(date=date):
                previous_durations_total += timelog.duration

            if (previous_durations_total + duration) > 1440:
                remaind_hours = (1440 - previous_durations_total) // 60
                remaind_miuntes = (1440 - previous_durations_total) % 60
                
                if remaind_miuntes or remaind_hours:
                    raise ValidationError(f'Your remaind duration for '
                                          f'{date} is {remaind_hours} hours and {remaind_miuntes} minutes.')
                else:
                    raise ValidationError(f'There is no time left for {date}')

            clean_data['duration'] = duration
        
        return clean_data


class SubjectForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.user_subjects = kwargs.pop('user_subjects')
        super().__init__(*args, **kwargs)
        # add bootstarp class to the fields
        for v in self.visible_fields():
            v.field.widget.attrs['class'] = 'form-control'
    class Meta:
        model = Subject
        fields = ['name', 'description']

    def clean(self):
        clean_data = super().clean()
        name = clean_data.get('name')
        if name:
            if name.lower() in [s.name for s in self.user_subjects]:
                raise ValidationError(f'{name.lower()} already exists.')
            clean_data['name'] = name.lower()

        return clean_data


class TagForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.user_tags = kwargs.pop('user_tags')
        super().__init__(*args, **kwargs)
        # add bootstarp class to the name field
        self.fields['name'].widget.attrs['class'] = 'form-control'

    class Meta:
        model = Tag
        fields = ['name']

    def clean(self):
        clean_data = super().clean()
        name = clean_data.get('name')
        if name:
            if name.lower() in [s.name for s in self.user_tags]:
                raise ValidationError(f'{name.lower()} already exists.')
            clean_data['name'] = name.lower()

        return clean_data