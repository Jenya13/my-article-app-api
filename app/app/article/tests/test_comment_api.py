""" 
Test for comment APIs.
"""

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from core.models import Article, Comment


def list_url(article_id):
    """Create and return comment list-create url."""
    return reverse('article:comment-list-create', args=[article_id])


def detail_url(article_id, comment_id):
    """Create and return comment url."""
    return reverse('article:comment-detail', args=[article_id, comment_id])


def create_article(user, **params):
    """Create and return a sample article."""
    defaults = {
        'title': 'Test title',
        'opening': 'Test opening',
        'content': 'Test article'
    }
    defaults.update(params)

    article = Article.objects.create(user=user, **defaults)
    return article


class PublicCommentAPITests(TestCase):
    """Tests unauthenticated API requests."""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test auth is required to call API."""

        user = get_user_model().objects.create_user(
            'Test',
            'Test',
            'user@example.com',
            'testpass123'
        )
        article = create_article(user)

        comment_data = {
            "content": "Test comment"
        }
        url = list_url(article.id)
        res = self.client.post(url, data=comment_data)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateCommentAPITests(TestCase):
    """Tests authenticated API requests."""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'Test',
            'Test',
            'user@example.com',
            'testpass123'
        )
        self.client.force_authenticate(self.user)

    def test_create_comment(self):
        """Test creation comment on article."""
        article = create_article(self.user)

        payload = {
            "content": "Test comment"
        }
        url = list_url(article.id)
        res = self.client.post(url, payload)

        article.refresh_from_db()
        comment = article.comments.first()

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(article.comments.count(), 1)
        self.assertEqual(comment.content, payload['content'])
