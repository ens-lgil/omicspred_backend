from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.views import exception_handler
from rest_framework.exceptions import Throttled
from rest_framework.serializers import ValidationError
from django.db.models import Prefetch, Q
from omicspred.models import *
from .serializers import *



def custom_exception_handler(exc, context):
    # Call REST framework's default exception handler first,
    # to get the standard error response.
    response = exception_handler(exc, context)

    # Over the fixed rate limit
    if isinstance(exc, Throttled): # check that a Throttled exception is raised
        response.data = { # custom response data
            'message': 'request limit exceeded',
            'availableIn': '%d seconds'%exc.wait
        }
    # Over the maximum number of results per page (limit parameter)
    elif isinstance(exc, ValidationError):
        formatted_exc = ''
        for type in exc.detail.keys():
            if formatted_exc != '':
                formatted_exc += '; '
            formatted_exc += exc.detail[type]
        response.data = { # custom response data
            'status_code': response.status_code,
            'message': formatted_exc
        }
    elif response.status_code == status.HTTP_404_NOT_FOUND:
        response.data = { # custom response data
            'status_code': status.HTTP_404_NOT_FOUND,
            'message': 'This REST endpoint does not exist'
        }
    elif response is not None:
        response.data = { # custom response data
            'status_code': response.status_code,
            'message': str(exc)
        }
    else:
        response.data = {
            'status_code': status.HTTP_500_INTERNAL_SERVER_ERROR,
            'message': 'Internal Server Error'
        }
    return response


def get_ids_list(object):
    ids_list = []

    # List of IDs provided in the URL
    ids = object.request.query_params.get('filter_ids')
    if ids and ids is not None:
        ids = ids.upper()
        ids_list = ids.split(',')
    # List of IDs provided in a JSON object
    elif 'filter_ids' in object.request.data:
        ids_list = [ x.upper() for x in object.request.data['filter_ids']]
    return ids_list


## Scores ##

class RestListScores(generics.ListAPIView):
    """
    Retrieve the Polygenic Scores
    """
    serializer_class = ScoreSerializer

    def get_queryset(self):
        # Fetch all the Scores
        # queryset = Score.objects.defer(*related_dict['score_defer']).select_related('publication').all().prefetch_related(*related_dict['score_prefetch']).order_by('num')
        queryset = Score.objects.select_related('publication','platform').all().order_by('num')

        # Filter by list of Score IDs
        ids_list = get_ids_list(self)
        if ids_list:
            queryset = queryset.filter(id__in=ids_list)

        return queryset


class RestScore(generics.RetrieveAPIView):
    """
    Retrieve one Polygenic Score (PGS)
    """

    def get(self, request, opgs_id):
        opgs_id = opgs_id.upper()
        try:
            queryset = Score.objects.select_related('publication','platform').get(id=opgs_id)
            # queryset = Score.objects.defer(*related_dict['score_defer']).select_related('publication').prefetch_related(*related_dict['score_prefetch']).get(id=pgs_id)
        except Score.DoesNotExist:
            queryset = None
        serializer = ScoreSerializer(queryset,many=False)
        return Response(serializer.data)


class RestScoreSearch(generics.ListAPIView):
    """
    Search the Polygenic Score(s) using query
    """
    serializer_class = ScoreSerializer

    def get_queryset(self):
        queryset = Score.objects.select_related('publication','platform').all().order_by('num')
        params = 0

        # Search by list of Score IDs
        opgs_ids = self.request.query_params.get('opgs_ids')
        if opgs_ids and opgs_ids is not None:
            opgs_ids = opgs_ids.upper()
            opgs_ids_list = opgs_ids.split(',')
            queryset = queryset.filter(id__in=opgs_ids_list)
            params += 1

        # Search by Pubmed ID
        pmid = self.request.query_params.get('pmid')
        if pmid and pmid.isnumeric():
            queryset = queryset.filter(publication__pmid=pmid)
            params += 1

        # Search by platform
        platform = self.request.query_params.get('platform')
        if platform and platform is not None:
            queryset = queryset.filter(platform__name__iexact=platform)
            params += 1

        if params == 0:
            queryset = []

        return queryset
