import math

from rest_framework.pagination import LimitOffsetPagination


class StandardResultsSetPagination(LimitOffsetPagination):
    page_size = 100
    page_size_query_param = 'page_size'
    max_page_size = 1000
    limit = 100

    def paginate_queryset(self, queryset, request, view=None):
        self.view = view
        return super().paginate_queryset(queryset, request, view)

    def get_paginated_response(self, data, *args, **kwargs):
        self.count = self.get_count(data)
        if not hasattr(self, 'offset'):
            self.offset = 0

        return {
            'count': self.count,
            'page_count': math.ceil(self.count / self.page_size),
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'content': data,
        }
