from urllib.request import Request
from django.db.models import QuerySet
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response
from rest_framework.serializers import ValidationError
from collections import OrderedDict
from omicspred.models import Score,Info


class CustomPagination(LimitOffsetPagination):

    min_limit = 1
    max_limit = 500
    #max_limit = 250

    def get_count(self, queryset: QuerySet) -> int:
        """
        Determine an object count, supporting either querysets or regular lists.
        Overwrite the LimitOffsetPagination.get_count() method to speed up
        the Score model count for the unfiltered /api/score/all endpoint
        """
        try:
            # Remove ordering from queryset to speed up the count() query
            if ' ORDER BY ' in str(queryset.query):
                queryset = queryset.order_by()
            # Replace the count() query with a faster query for the Score model when no filters are applied
            if queryset.model is Score and ' WHERE ' not in str(queryset.query):
                scores_count = Info.objects.get(name='scores')
                return scores_count.value
            return queryset.count()
        except (AttributeError, TypeError):
            return len(queryset)


    def get_paginated_response(self, data: list) -> Response:
        ''' Customise the head of the pagination response '''
        return Response(OrderedDict([
            ('size', len(data)),
            ('count', self.count),
            ('next', self.get_next_link()),
            ('previous', self.get_previous_link()),
            ('results', data)
        ]))


    def paginate_queryset(self, queryset: QuerySet, request: Request, view=None):
        ''' Set a maximum value (limit) on the number of results returned per page '''
        limit = request.query_params.get('limit')
        if limit:
            limit = int(limit)
            error_msg = None
            error_dict = {}
            if limit > self.max_limit:
                error_msg = f'URL parameter \'limit\' should be less than or equal to {self.max_limit}'
            elif limit < self.min_limit:
                error_msg = f'URL parameter \'limit\' should be greater than or equal to {self.min_limit}'
            if error_msg:
                error_dict['limit'] = error_msg
                raise ValidationError(error_dict)

        return super(self.__class__, self).paginate_queryset(queryset, request, view)
