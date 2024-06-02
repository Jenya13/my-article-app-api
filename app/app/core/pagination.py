""" 
Pagination for API's lists.
"""

from rest_framework.pagination import PageNumberPagination, LimitOffsetPagination


class ArticlePagination(PageNumberPagination):
    """Pagination class for articles list."""
    page_size = 7
    page_query_param = 'page'


class CommentPagination(LimitOffsetPagination):
    """Pagination class for article comments list."""
    default_limit = 5
    max_limit = 100
