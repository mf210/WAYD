from django.urls import path

from . import views


app_name = 'timing'
urlpatterns = [
    path('', views.index, name='index'),
    path('home/', views.home, name='home'),
    # timelogs
    path('timelogs/', views.timelogs, name='timelogs'),
    path('timelogs/<uuid:pk>/', views.timelog_detail, name='timelog-detail'),
    path('timelogs/delete/<uuid:pk>/', views.timelog_delete, name='timelog-delete'),
    # subjects
    path('subjects/', views.subjects, name='subjects'),
    path('subjects/<uuid:pk>/', views.subject_detail, name='subject-detail'),
    path('subjects/delete/<uuid:pk>/', views.subject_delete, name='subject-delete'),
    # tags
    path('tags/', views.tags, name='tags'),
    path('tags/<uuid:pk>/', views.tag_detail, name='tag-detail'),
    path('tags/delete/<uuid:pk>/', views.tag_delete, name='tag-delete')
]