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
    'score':       'rest/score/',
    'table':       'rest/table/',
    'plot':        'rest/plot/',
    'test':        'rest/test/',
}

urlpatterns = [
    # Cohorts
    re_path(r'^'+rest_urls['cohort']+'all'+slash, cache_page(cache_time)(RestListCohorts.as_view()), name="getAllCohorts"),
    # Performance metrics
    re_path(r'^'+rest_urls['performance']+'all'+slash, cache_page(cache_time)(RestListPerformances.as_view()), name="getAllPerformanceMetrics"),
    re_path(r'^'+rest_urls['performance']+'search'+slash, RestPerformanceSearch.as_view(), name="searchPerformanceMetrics"),
    # Publication
    re_path(r'^'+rest_urls['publication']+'all'+slash, cache_page(cache_time)(RestListPublications.as_view()), name="getAllPublications"),
    re_path(r'^'+rest_urls['publication']+'search'+slash, cache_page(cache_time)(RestPublicationSearch.as_view()), name="searchPublications"),
    # Samples
    re_path(r'^'+rest_urls['sample']+'all'+slash, cache_page(cache_time)(RestListSamples.as_view()), name="getAllSamples"),
    # Scores
    re_path(r'^'+rest_urls['score']+'all'+slash, cache_page(cache_time)(RestListScores.as_view()), name="getAllScores"),
    re_path(r'^'+rest_urls['score']+'searchbygene/(?P<gene>[^/]+)'+slash, RestScoreSearchByGene.as_view(), name="searchScoresByGene"),
    re_path(r'^'+rest_urls['score']+'searchbyprotein/(?P<protein>[^/]+)'+slash, RestScoreSearchByProtein.as_view(), name="searchScoresByProtein"),
    re_path(r'^'+rest_urls['score']+'searchbymetabolite/(?P<metabolite>[^/]+)'+slash, RestScoreSearchByMetabolite.as_view(), name="searchScoresByMetabolite"),
    re_path(r'^'+rest_urls['score']+'search'+slash, RestScoreSearch.as_view(), name="searchScores"),
    re_path(r'^'+rest_urls['score']+'(?P<opgs_id>[^/]+)'+slash, RestScore.as_view(), name="getScore"),
    # Platform
    re_path(r'^'+rest_urls['platform']+'all'+slash, cache_page(cache_time)(RestListPlatforms.as_view()), name="getAllPlatforms"),
    re_path(r'^'+rest_urls['table']+'search'+slash, cache_page(cache_time)(RestTableSearch.as_view()), name="searchTables"),
    re_path(r'^'+rest_urls['table']+'metabolite/search'+slash, cache_page(cache_time)(RestMetaboliteTableSearch.as_view()), name="searchMetaboliteTables"),
    re_path(r'^'+rest_urls['table']+'protein/search'+slash, cache_page(cache_time)(RestProteinTableSearch.as_view()), name="searchProteinTables"),
    re_path(r'^'+rest_urls['table']+'transcript/search'+slash, cache_page(cache_time)(RestTranscriptTableSearch.as_view()), name="searchEnsemblTables"),
    # Plot
    re_path(r'^'+rest_urls['plot']+'search'+slash, cache_page(cache_time)(RestPlotSearch.as_view()), name="searchPlots"),
    # Test
    re_path(r'^'+rest_urls['test']+'metabolite/'+slash, cache_page(cache_time)(RestTestMetabolite.as_view()), name="searchTestMetabolite"),
    re_path(r'^'+rest_urls['test']+'protein/'+slash, cache_page(cache_time)(RestTestProtein.as_view()), name="searchTestProtein"),
    re_path(r'^'+rest_urls['test']+'transcript/'+slash, cache_page(cache_time)(RestTestTranscript.as_view()), name="searchTestTranscript"),
]
