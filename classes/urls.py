from django.urls import path, re_path
from .views import *

app_name='classes'
urlpatterns = [
    path('list/', majorLV.as_view(), name= 'major_list'),
    #re_path(r'^major/(?P<slug>[-\w]+)/$', majorDV.as_view(), name='major_detail'),
]