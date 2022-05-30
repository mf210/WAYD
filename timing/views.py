import datetime
from random import randint

from django.shortcuts import redirect, render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Max, Min
from django.core.paginator import Paginator
from django.contrib import messages

from .forms import DateForm, TimeLogForm, SubjectForm, TagForm



def index(request):
    if request.user.is_authenticated:
        return redirect('timing:home')
    return render(request, 'index.html')


@login_required
def home(request):
    user_timelogs = request.user.timelogs
    # get min and max date from user's timelogs
    min_date, max_date = user_timelogs.aggregate(Min('date'), Max('date')).values()
    date_form = DateForm(min_date=min_date, max_date=max_date)
    if request.GET.get('start') and request.GET.get('end'):
        date_form = DateForm(request.GET, min_date=min_date, max_date=max_date)
        if date_form.is_valid():
            # overwrite the min and max dates with user's specified dates
            form_dates = date_form.clean()
            min_date, max_date = form_dates['start'], form_dates['end']
    
    dates = create_date_list(min_date, max_date)
    available_dates = set(user_timelogs.filter(date__range=(min_date, max_date))\
                          .values_list('date', flat=True).distinct())
    user_subjects = request.user.subject_set.all().order_by('last_modified')
    user_tags = request.user.tag_set.all().order_by('last_modified')
    context = {
        'date_based_chart_data': create_date_based_chart_data(user_subjects, dates, available_dates),
        'subject_based_chart_data': create_subject_based_chart_data(user_subjects, min_date, max_date),
        'tag_based_chart_data':  create_tag_based_chart_data(user_tags, min_date, max_date),
        'timelogs': user_timelogs.all()[:10],
        'date_form': date_form
    }
    return render(request, 'timing/home.html', context)


@login_required
def timelogs(request):
    # timelog form
    user = request.user
    timelog_form = TimeLogForm(registrant_user=user)
    if request.method == 'POST':
        timelog_form = TimeLogForm(data=request.POST, registrant_user=user)
        if timelog_form.is_valid():
            # if form is valid, add the user and calculated duration to timelog obj then save it 
            duration = timelog_form.clean()['duration']
            timelog = timelog_form.save(commit=False)
            timelog.user = user
            timelog.duration = duration
            timelog.save()
            timelog_form.save_m2m()
            messages.add_message(
                    request, level=250,
                    message='Record successfully added!',
                    extra_tags='success')
            return redirect('timing:timelogs')

    # pagination the timelog records
    page_num = request.GET.get('page')
    paginator = Paginator(request.user.timelogs.all(), per_page=10)
    page_obj = paginator.get_page(page_num)

    context = {
        'page_obj': page_obj,
        'page_range': paginator.get_elided_page_range(page_obj.number),
        'timelog_form': timelog_form
    }
    return render(request, 'timing/timelogs_list.html', context)


@login_required
def timelog_detail(request, pk):
    timelog = get_object_or_404(request.user.timelogs.all(), pk=pk)
    context = {
        'timelog': timelog
    }
    return render(request, 'timing/timelog_detail.html', context)


@login_required
def timelog_delete(request, pk):
    timelog = get_object_or_404(request.user.timelogs.all(), pk=pk)
    if request.method == 'POST':
        timelog.delete()
        messages.add_message(request, level=250, extra_tags='success',
                             message='Record successfully deleted!')
        return redirect('timing:timelogs')

    context = {'timelog': timelog}
    return render(request, 'timing/timelog_delete.html', context)


@login_required
def subjects(request):
    all_user_subjects = request.user.subject_set.all()
    subject_form = SubjectForm(user_subjects=all_user_subjects)
    if request.method == 'POST':
        subject_form = SubjectForm(data=request.POST, user_subjects=all_user_subjects)
        if subject_form.is_valid():
            subject = subject_form.save(commit=False)
            subject.user = request.user
            subject.save()
            messages.add_message(
                request, level=250,
                message=f'Subject "{subject.name}" successfully added!',
                extra_tags='success')
            return redirect('timing:subjects')

    # pagination
    page_num = request.GET.get('page')
    paginator = Paginator(all_user_subjects, per_page=10)
    page_obj = paginator.get_page(page_num)

    context = {
        'page_obj': page_obj,
        'page_range': paginator.get_elided_page_range(page_obj.number),
        'subject_form': subject_form
    }
    return render(request, 'timing/subjects.html', context)


@login_required
def subject_detail(request, pk):
    subject = get_object_or_404(request.user.subject_set.all(), pk=pk)
    user_subjects = request.user.subject_set.exclude(pk=pk)
    subject_form = SubjectForm(instance=subject, user_subjects=user_subjects)
    if request.method == 'POST':
        subject_form = SubjectForm(
            instance=subject,
            user_subjects=user_subjects,
            data=request.POST
        )
        if subject_form.is_valid():
            subject_form.save()
            messages.add_message(
                request, level=250, extra_tags='success',
                message='subject successfully updated!'
            )
            return redirect('timing:subject-detail', pk=pk)

    context = {'subject_form': subject_form}
    return render(request, 'timing/subject_detail.html', context)


@login_required
def subject_delete(request, pk):
    subject = get_object_or_404(request.user.subject_set.all(), pk=pk)
    if request.method == 'POST':
        subject.delete()
        messages.add_message(request, level=250, extra_tags='success',
                             message=f'Subject "{subject.name}" successfully deleted!')
        return redirect('timing:subjects')
    
    context = {'subject': subject}
    return render(request, 'timing/subject_delete.html', context)


@login_required
def tags(request):
    all_user_tags = request.user.tag_set.all()
    tag_form = TagForm(user_tags=all_user_tags)
    if request.method == 'POST':
        tag_form = TagForm(data=request.POST, user_tags=all_user_tags)
        if tag_form.is_valid():
            tag = tag_form.save(commit=False)
            tag.user = request.user
            tag.save()
            messages.add_message(
                request, level=250,
                message=f'Tag "{tag.name}" successfully added!',
                extra_tags='success')
            return redirect('timing:tags')

    # pagination
    page_num = request.GET.get('page')
    paginator = Paginator(all_user_tags, per_page=10)
    page_obj = paginator.get_page(page_num)

    context = {
        'page_obj': page_obj,
        'page_range': paginator.get_elided_page_range(page_obj.number),
        'tag_form': tag_form
    }
    return render(request, 'timing/tags.html', context)


@login_required
def tag_detail(request, pk):
    tag = get_object_or_404(request.user.tag_set.all(), pk=pk)
    user_tags = request.user.tag_set.exclude(pk=pk)
    tag_form = TagForm(instance=tag, user_tags=user_tags)
    if request.method == 'POST':
        tag_form = TagForm(
            instance=tag,
            user_tags=user_tags,
            data=request.POST
        )
        if tag_form.is_valid():
            tag_form.save()
            messages.add_message(
                request, level=250, extra_tags='success',
                message='tag successfully updated!'
            )
            return redirect('timing:tag-detail', pk=pk)

    context = {'tag_form': tag_form}
    return render(request, 'timing/tag_detail.html', context)


@login_required
def tag_delete(request, pk):
    tag = get_object_or_404(request.user.tag_set.all(), pk=pk)
    if request.method == 'POST':
        tag.delete()
        messages.add_message(request, level=250, extra_tags='success',
                             message=f'Tag "{tag.name}" successfully deleted!')
        return redirect('timing:tags')
    
    context = {'tag': tag}
    return render(request, 'timing/tag_delete.html', context)


def create_date_based_chart_data(subjects, dates, available_dates):
    # create json data for date based chart (stacked bar chart)
    datasets = []
    # create dataset and add them to the datasets list
    for subject in subjects:
        dataset = {}
        # generate random color for each dataset
        dataset['backgroundColor'] = f'rgb({randint(0, 255)},{randint(0, 255)},{randint(0, 255)})'
        dataset['label'] = subject.name
        dataset['data'] = []
        # get all related timelogs with each date and sum up the duration time (based on minutes)
        for date in dates:
            spent_mins = 0
            # don't hit the database for each date that doesn't exisit
            if date in available_dates:
                for timelog in subject.timelog_set.filter(date=date):
                    spent_mins += timelog.duration
                # add the sum of timelogs duration based on hours to the data
                dataset['data'].append(round((spent_mins / 60), 1))
            else:
                dataset['data'].append(0)

        datasets.append(dataset)

    return {'labels': [d.isoformat() for d in dates], 'datasets': datasets}


def create_subject_based_chart_data(subjects, min_date, max_date):
    # create json data for subject based chart (doughnut chart)
    labels = []
    dataset = {
        'data': [],
        'backgroundColor': []
    }
    for subject in subjects:
        labels.append(subject.name)
        spent_mins = 0
        for timelog in subject.timelog_set.filter(date__range=(min_date, max_date)):
            spent_mins += timelog.duration
        
        dataset['data'].append(round((spent_mins / 60), 1))
        dataset['backgroundColor'].append(f'rgb({randint(0, 255)},{randint(0, 255)},{randint(0, 255)})')
    
    # sort the labels and data
    labels = [label for label, _ in sorted(zip(labels, dataset['data']), key=lambda t: t[1], reverse=True)]
    dataset['data'].sort(reverse=True)

    return {'labels': labels, 'datasets': [dataset]}


def create_tag_based_chart_data(tags, min_date, max_date):
    # create json data for tag based chart (horizontal bar chart)
    labels = []
    dataset = {
        'data': [],
        'backgroundColor': []
    }
    for tag in tags:
        labels.append(tag.name)
        spent_mins = 0
        for timelog in tag.timelog_set.filter(date__range=(min_date, max_date)):
            spent_mins += timelog.duration
        
        dataset['data'].append(round((spent_mins / 60), 1))
        dataset['backgroundColor'].append(f'rgb({randint(0, 255)},{randint(0, 255)},{randint(0, 255)})')
    
    # sort the labels and data
    labels = [label for label, _ in sorted(zip(labels, dataset['data']), key=lambda t: t[1], reverse=True)]
    dataset['data'].sort(reverse=True)
    
    return {'labels': labels, 'datasets': [dataset]}


def create_date_list(min_date, max_date):
    if min_date and max_date:
        dates = [min_date]
        while min_date < max_date:
            min_date += datetime.timedelta(days=1)
            dates.append(min_date)
        return dates
    return []