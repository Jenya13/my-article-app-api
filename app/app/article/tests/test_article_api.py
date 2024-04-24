"""
Test for article APIs.
"""

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from core.models import Article
from article.serializers import (ArticleSerializer, ArticleDetailSerializer)

ARTICLE_URL = reverse('article:article-list')


def detail_url(article_id):
    """Create and return article url."""
    return reverse('article:article-detail', args=[article_id])


def create_article(user, **params):
    """Create and return a sample article."""
    defaults = {
        'title': 'Test title',
        'content': 'Test article'
    }
    defaults.update(params)

    article = Article.objects.create(user=user, **defaults)
    return article


class PublicArticleAPITests(TestCase):
    """Tests unauthenticated API requests."""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test auth is required to call API."""
        res = self.client.get(ARTICLE_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateArticleAPITests(TestCase):
    """Tests authenticated API requests."""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'user@example.com',
            'testpass123'
        )
        self.client.force_authenticate(self.user)

    def test_retriev_articles(self):
        """Test retrieving a list of articles."""
        create_article(user=self.user)
        create_article(user=self.user)

        res = self.client.get(ARTICLE_URL)

        articles = Article.objects.all().order_by('-id')
        serializer = ArticleSerializer(articles, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_article_list_limited_to_user(self):
        """Test list of articles is limited to authenticated user."""
        other_user = get_user_model().objects.create_user(
            'other@example.com',
            'passtest123',
        )

        create_article(user=other_user)
        create_article(user=self.user)

        res = self.client.get(ARTICLE_URL)

        articles = Article.objects.filter(user=self.user)
        serializer = ArticleSerializer(articles, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_get_article_detail(self):
        """Test get article detail."""
        article = create_article(user=self.user)

        url = detail_url(article.id)
        res = self.client.get(url)

        serializer = ArticleDetailSerializer(article)
        self.assertEqual(res.data, serializer.data)

    def test_create_article(self):
        """Test create article."""

        payload = {
            'title': 'Test title',
            'content': 'some content'
        }

        res = self.client.post(ARTICLE_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        article = Article.objects.get(id=res.data['id'])

        for k, v in payload.items():
            self.assertEqual(getattr(article, k), v)

        self.assertEqual(article.user, self.user)
