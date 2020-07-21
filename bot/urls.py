from django.urls import path

from . import views

urlpatterns = [
    path('messages', views.index, name='index'),
    path('notify', views.notify, name='notify'),
]