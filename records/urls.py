from django.urls import path
from . import views

app_name = 'records'
urlpatterns = [
    path('', views.home, name='home'),
    path('create/', views.create_record, name='create'),
    path('upload/', views.upload_file, name='upload'),
    path('data/', views.view_data, name='view_data'),
    path('data/search/', views.ajax_search, name='ajax_search'),
    path('data/<int:pk>/edit/', views.edit_record, name='edit_record'),
    path('data/<int:pk>/delete/', views.delete_record, name='delete_record'),
]
