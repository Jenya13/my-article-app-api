""" 
Tests for models.
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from core import models


def create_user(first_name="First", last_name="Last", email='user@example.com', password='testpass123'):
    """Create and return a new user"""
    return get_user_model().objects.create_user(email, password)


class ModelTests(TestCase):
    """Test models."""

    def test_create_user_with_email_successful(self):
        """Test creating a user with email successful."""
        first_name = 'First'
        last_name = 'Last'
        email = 'test@example.com'
        password = 'pass12345'
        user = get_user_model().objects.create_user(first_name=first_name,
                                                    lastname=last_name, email=email, password=password)

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_new_user_test_normalized(self):
        """Test email is normalized for neew user."""
        sample_emails = [
            ['test1@EXAMPLE.com', 'test1@example.com'],
            ['Test2@Example.com', 'Test2@example.com'],
            ['TEST3@EXAMPLE.COM', 'TEST3@example.com'],
            ['test4@example.COM', 'test4@example.com'],
        ]

        for email, expected in sample_emails:
            user = get_user_model().objects.create_user(email, 'sample123')
            self.assertEqual(user.email, expected)

    def test_new_user_without_email_raises_error(self):
        """Test that creating a user without email raises ValueError."""
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user('', 'test123')

    def test_create_superuser(self):
        """Test crating a superuser."""
        user = get_user_model().objects.create_superuser('test@example.com', 'test123')

        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)

    def test_create_article(self):
        """Test creating an article is successful."""
        user = get_user_model().objects.create_user('test@example.com', 'testpass123')
        article = models.Article.objects.create(
            user=user, title="Test title", content="Test article content.")
        self.assertEqual(str(article), article.title)

    def test_create_topic(self):
        """Test creating topic successful."""
        user = create_user()
        topic = models.Topic.objects.create(user=user, name="Topic test'")
        self.assertEqual(str(topic), topic.name)

    def test_create_comment(self):
        """Test creating comment successful."""
        user = create_user()
        comment = models.Comment.objects.create(
            user=user, content="test comment content")
        self.assertEqual(str(comment), comment.content)
