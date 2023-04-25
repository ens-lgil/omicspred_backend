from django.urls import path, re_path
from django.views.generic import TemplateView
from django.views.decorators.cache import cache_page
from .views import *


# Seconds * Minutes
#cache_time = 60 * 2
cache_time = 0

slash = '/?'

rest_urls = {
    'cohort':      'rest/cohort/',
    'platform':    'rest/platform/',
    'performance': 'rest/performance/',
    'publication': 'rest/publication/',
    'release':     'rest/release/',
    'sample':      'rest/sample/',
    'score':       'rest/score/'
}

urlpatterns = [
    # Scores
    re_path(r'^'+rest_urls['score']+'all'+slash, cache_page(cache_time)(RestListScores.as_view()), name="getAllScores"),
    re_path(r'^'+rest_urls['score']+'search'+slash, RestScoreSearch.as_view(), name="searchScores"),
    re_path(r'^'+rest_urls['score']+'(?P<opgs_id>[^/]+)'+slash, RestScore.as_view(), name="getScore"),
]
