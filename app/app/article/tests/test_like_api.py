""" 
Test for likes APIs.
"""

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from core.models import Article, Like


def list_url(article_id):
    """Create or return likes, list-create url."""
    return reverse('article:like-list-create', args=[article_id])


def delete_url(article_id):
    """Delete url."""
    return reverse('article:like-delete', args=[article_id])


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


class PublicLikeAPITests(TestCase):

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

        url = list_url(article.id)
        res = self.client.post(url)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateLikeAPITests(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'Test',
            'Test',
            'user@example.com',
            'testpass123'
        )
        self.client.force_authenticate(self.user)

    def test_user_like_article(self):
        """Test user create like for article he liked."""
        article = create_article(user=self.user)

        other_user = get_user_model().objects.create_user(
            'user', 'other', 'other@example.com', 'test123'
        )
        self.client.force_authenticate(other_user)
        url = list_url(article.id)
        res = self.client.post(url)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

    def test_user_unable_like_article_twice(self):
        """Test user unable to create more then one like for article he liked."""
        article = create_article(user=self.user)

        url = list_url(article.id)
        res1 = self.client.post(url)
        res2 = self.client.post(url)

        self.assertEqual(res1.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res2.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Like.objects.filter(
            user=self.user, article_id=article.id).count(), 1)

    def test_user_unliked_liked_article(self):
        """Test user remove like from article he liked before."""
        article = create_article(user=self.user)

        url = list_url(article.id)
        res1 = self.client.post(url)

        self.assertEqual(res1.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Like.objects.filter(
            user=self.user, article_id=article.id).count(), 1)

        del_url = delete_url(article.id)
        res2 = self.client.delete(del_url)

        self.assertEqual(res2.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Like.objects.filter(
            user=self.user, article_id=article.id).count(), 0)

    def test_user_unable_unlike_article_twice(self):
        """Test user remove unable to remove like more then once from article that he liked."""
        article = create_article(user=self.user)

        url = list_url(article.id)
        res1 = self.client.post(url)

        self.assertEqual(res1.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Like.objects.filter(
            user=self.user, article_id=article.id).count(), 1)

        del_url = delete_url(article.id)
        res2 = self.client.delete(del_url)
        res3 = self.client.delete(del_url)

        self.assertEqual(res3.status_code, status.HTTP_404_NOT_FOUND)

    def test_retrieve_likes(self):
        """Test like retrieve for article."""

        article = create_article(user=self.user)

        url = list_url(article.id)
        like_res1 = self.client.post(url)

        other_user = get_user_model().objects.create_user(
            'user', 'other', 'other@example.com', 'test123'
        )
        self.client.force_authenticate(other_user)
        like_res2 = self.client.post(url)

        likes_list_res = self.client.get(url)

        self.assertEqual(likes_list_res.status_code, status.HTTP_200_OK)
        likes_count = Like.objects.filter(
            article_id=article.id).count()
        self.assertEqual(len(likes_list_res.data), likes_count)
