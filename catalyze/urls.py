from django.conf.urls import include, url
from . import views


urlpatterns = [
    url(r'callback', views.callback, name='catalyze.callback'),
    url(r'$', views.index, name='catalyze.index'),
]
