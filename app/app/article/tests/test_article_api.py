"""
Test for article APIs.
"""

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from core.models import Article, Topic
from article.serializers import (ArticleSerializer, ArticleDetailSerializer)

ARTICLE_URL = reverse('article:article-list')


def detail_url(article_id):
    """Create and return article url."""
    return reverse('article:article-detail', args=[article_id])


def list_url():
    """Create and return all articles url."""
    return reverse('article:articles-all')


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

    def test_unauthorized_user_retriev_all_articles(self):
        """Test retrieving a list of articles."""
        user1 = get_user_model().objects.create_user(
            'user1@example.com',
            'testpass123'
        )
        user2 = get_user_model().objects.create_user(
            'user2@example.com',
            'testpass123'
        )
        create_article(user=user1)
        create_article(user=user2)

        url = list_url()

        res = self.client.get(url)

        articles = Article.objects.all().order_by('-id')
        serializer = ArticleSerializer(articles, many=True)

        # Sort both lists by 'id' before comparison
        res_data_sorted = sorted(res.data, key=lambda x: x['id'])
        serializer_data_sorted = sorted(serializer.data, key=lambda x: x['id'])

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res_data_sorted, serializer_data_sorted)


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

    def test_create_article_with_new_topics(self):
        """Test creating article with new topics."""

        payload = {
            'title': 'Test title',
            'content': 'some content',
            'topics': [{'name': 'topic 1'}, {'name': 'topic 2'}]
        }
        res = self.client.post(ARTICLE_URL, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        articles = Article.objects.filter(user=self.user)
        self.assertEqual(articles.count(), 1)
        article = articles[0]
        self.assertEqual(article.topics.count(), 2)

        for topic in payload['topics']:
            exists = article.topics.filter(
                name=topic['name'], user=self.user).exists()
            self.assertTrue(exists)

    def test_create_article_with_existing_topic(self):
        """Test creating an article with existing topic."""
        topic_software = Topic.objects.create(user=self.user, name='Software')
        payload = {
            'title': 'Some software article',
            'content': 'Article content about software',
            'topics': [{'name': 'Software'}, {'name': 'other topic'}]
        }
        res = self.client.post(ARTICLE_URL, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        articles = Article.objects.filter(user=self.user)
        self.assertEqual(articles.count(), 1)
        article = articles[0]
        self.assertEqual(article.topics.count(), 2)
        self.assertIn(topic_software, article.topics.all())
        for topic in payload['topics']:
            exists = article.topics.filter(
                name=topic['name'], user=self.user).exists()
            self.assertTrue(exists)

    def test_create_topic_on_update(self):
        """Test creating topic when updating an article."""
        article = create_article(user=self.user)

        payload = {
            'topics': [{'name': 'Software'}]
        }

        url = detail_url(article.id)
        res = self.client.patch(url, payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        new_topic = Topic.objects.get(user=self.user, name='Software')
        self.assertIn(new_topic, article.topics.all())

    def test_update_article_assign_topic(self):
        """Test assigning an existing topic when updating an article."""
        topic_finance = Topic.objects.create(user=self.user, name='Finance')
        article = create_article(user=self.user)
        article.topics.add(topic_finance)

        topic_money = Topic.objects.create(user=self.user, name='Money')
        payload = {
            'topics': [{'name': 'Money'}]
        }
        url = detail_url(article.id)
        res = self.client.patch(url, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn(topic_money, article.topics.all())
        self.assertNotIn(topic_finance, article.topics.all())
