""" 
Serializers for Article API.
"""
from core.models import Article
from rest_framework import serializers


class ArticleSerializer(serializers.ModelSerializer):
    """Serializer for article."""

    class Meta:
        model = Article
        fields = ['id', 'title',  'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class ArticleDetailSerializer(ArticleSerializer):
    """Serializer for detail view."""

    class Meta(ArticleSerializer.Meta):
        fields = ArticleSerializer.Meta.fields + ['content']
