"""
Test for article topics APIs.
"""

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from core.models import Topic
from article.serializers import TopicSerializer  # ArticleDetailSerializer)


TOPIC_URL = reverse('article:topic-list')


def detail_url(topic_id):
    """Create and return a topic detail url."""
    return reverse('article:topic-detail', args=[topic_id])


def create_user(first_name='First', last_name='Last', email='user@example.com', password='testpass123'):
    """Create and return a user."""
    return get_user_model().objects.create_user(first_name, last_name, email, password)


class PublicTopicAPITests(TestCase):
    """Test unauthenticated API requests."""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test auth is required for retrieving topics."""
        res = self.client.get(TOPIC_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivetTopicAPITests(TestCase):
    """Test authenticated API requests."""

    def setUp(self):
        self.user = create_user()
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_retrieve_topics(self):
        """Test retrieving a list of topics."""
        Topic.objects.create(user=self.user, name='Test topic 1')
        Topic.objects.create(user=self.user, name='Test topic 2')

        res = self.client.get(TOPIC_URL)

        topics = Topic.objects.all().order_by('-name')
        serializer = TopicSerializer(topics, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_topics_limited_to_user(self):
        """Test list of topics is limited to authenticated user."""
        user2 = create_user(first_name='Testf',
                            last_name='Testl', email='user2@example.com')
        Topic.objects.create(user=user2, name='Test topic 3')
        topic = Topic.objects.create(user=self.user, name='Test topic 4')

        res = self.client.get(TOPIC_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], topic.name)
        self.assertEqual(res.data[0]['id'], topic.id)

    def test_update_topic(self):
        """Test updating topic."""
        topic = Topic.objects.create(user=self.user, name='Test topic')

        payload = {
            'name': 'Updated topic'
        }

        url = detail_url(topic.id)
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        topic.refresh_from_db()
        self.assertEqual(topic.name, payload['name'])

    def test_delete_topic(self):
        """Test topic deleted."""
        topic = Topic.objects.create(user=self.user, name='Test topic del')

        url = detail_url(topic.id)

        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        topics = Topic.objects.filter(user=self.user)
        self.assertFalse(topics.exists())
