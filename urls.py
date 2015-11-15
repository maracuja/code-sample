from django.conf.urls import patterns, url
from rest_framework.urlpatterns import format_suffix_patterns
import views

urlpatterns = patterns(
    '',

    url(r'^receive/$',
        views.Receive.as_view(), name='receive_translation'),
)

urlpatterns = format_suffix_patterns(urlpatterns)
