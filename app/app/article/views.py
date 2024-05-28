""" 
Views for article APIs.
"""

from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework import viewsets, mixins
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.shortcuts import get_object_or_404
from core.models import Article, Comment, Topic, Like
from article import serializers, permissions


class LikeListCreateView(generics.ListCreateAPIView):
    """View for list or create likes for article. """

    # queryset = Like.objects.all()
    serializer_class = serializers.LikeSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Gets all the likes for specific article."""

        article_id = self.kwargs['pk']
        return Like.objects.filter(article_id=article_id)

    def perform_create(self, serializer):
        """Method for like creation."""

        article_id = self.kwargs['pk']
        serializer.save(user=self.request.user, article_id=article_id)


class LikeDestroyView(generics.DestroyAPIView):
    """View for deleting like that have been set to an article."""

    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_object(self):
        """Get the like that user set to an article."""

        user = self.request.user
        article_id = self.kwargs['pk']
        like = Like.objects.filter(user=user, article_id=article_id).first()
        if not like:
            return None
        return like

    def delete(self, request, *args, **kwargs):
        """Delete method for like that has been set."""

        instance = self.get_object()
        if instance is None:
            return Response({'detail': 'Like not found.'}, status=status.HTTP_404_NOT_FOUND)
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)


class CommentListCreateView(generics.ListCreateAPIView):
    """Retrieve or create comments view."""

    queryset = Comment.objects.all()
    serializer_class = serializers.CommentSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        This method filters the queryset to only include comments related to a specific article.
        """
        article_id = self.kwargs.get(
            'pk')
        return Comment.objects.filter(article_id=article_id)

    def perform_create(self, serializer):
        """
        Method for creating a comment.
        """
        article_id = self.kwargs.get(
            'pk')

        serializer.save(user=self.request.user, article_id=article_id)


class CommentRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    """View to retrieve update or delete comment."""

    queryset = Comment.objects.all()
    serializer_class = serializers.CommentSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated, permissions.IsOwnerOrReadOnly]

    def get_object(self):
        """Get comment object."""
        comment_id = self.kwargs.get('pk')
        obj = get_object_or_404(Comment, id=comment_id)
        self.check_object_permissions(self.request, obj)
        return obj


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

    def get_permissions(self):
        if self.action == 'retrieve':
            return [permissions.IsAuthenticatedForRetrieve()]
        return [AllowAny()]

    def list(self, request):
        articles = Article.objects.all()
        serializer = serializers.ArticleSerializer(articles, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk='pk'):
        article = Article.objects.get(pk=pk)
        serializer = serializers.ArticleDetailSerializer(article)
        return Response(serializer.data)


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
