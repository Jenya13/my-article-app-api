""" 
Views for article APIs.
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import viewsets, mixins
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import Article, Topic
from article import serializers


class ArticleMVS(viewsets.ModelViewSet):
    """View for manage article APIs."""
    serializer_class = serializers.ArticleDetailSerializer
    queryset = Article.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Retrieve articles for authenticated user."""
        return self.queryset.filter(user=self.request.user).order_by('-id')

    def get_serializer_class(self):
        """Return the serializer class for request."""
        if self.action == 'list':
            return serializers.ArticleSerializer
        return self.serializer_class

    def perform_create(self, serializer):
        """Create a new article."""
        serializer.save(user=self.request.user)


class ArticleVS(viewsets.ViewSet):
    """View to retrieve a list of all articles for all users or specific article for authenticated user."""

    # to add permissions

    def list(self, request):
        articles = Article.objects.all()
        serializer = serializers.ArticleSerializer(articles, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk='pk'):
        article = Article.objects.get(pk=pk)
        serializer = serializers.ArticleSerializer(article)
        return Response(serializer.data)


# class ArticleVS(APIView):
#     """View to retrieve a list of all articles and."""

#     def get(self, request):
#         articles = Article.objects.all()
#         serializer = serializers.ArticleSerializer(articles, many=True)
#         return Response(serializer.data)


class TopicViewSet(mixins.ListModelMixin,
                   mixins.UpdateModelMixin,
                   mixins.DestroyModelMixin,
                   viewsets.GenericViewSet):
    """Manage tags in the database."""
    serializer_class = serializers.TopicSerializer
    queryset = Topic.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Retrieve topics for authenticated user."""
        return self.queryset.filter(user=self.request.user).order_by('-id')
