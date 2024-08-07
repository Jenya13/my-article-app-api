""" 
Database models.
"""
from django.conf import settings
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin


def user_profile_pic_path(instance, filename):
    """Generate file path for new user profile picture."""
    ext = filename.split('.')[-1]
    # The new file name will be user_id_profile_pic.ext
    filename = f'user_{instance.id}_profile_pic.{ext}'
    return f'profile_pics/{filename}'


def article_pic_path(instance, filename):
    """Generate file path for article picture."""
    ext = filename.split('.')[-1]
    # The new file name will be user_id_profile_pic.ext
    filename = f'user_article_{instance.id}_pic.{ext}'
    return f'article_pic/{filename}'


class UserManager(BaseUserManager):
    """User managment model."""

    def create_user(self, first_name, last_name, email, password=None, **extra_fields):
        """Create, save and return user"""
        if not email:
            raise ValueError("User must have email address.")
        user = self.model(
            first_name=first_name, last_name=last_name, email=self.normalize_email(email), **extra_fields)

        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, first_name, last_name, email, password):
        """Create and return superuser."""
        user = self.create_user(first_name, last_name, email, password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)

        return user


class User(AbstractBaseUser, PermissionsMixin):
    """Todos application User model."""
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    email = models.EmailField(max_length=255, unique=True)
    bio = models.TextField(blank=True)
    contact_me = models.CharField(max_length=255, blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    image = models.ImageField(
        upload_to=user_profile_pic_path, blank=True, null=True)
    objects = UserManager()

    USERNAME_FIELD = 'email'


class Article(models.Model):
    """Article model object."""
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    opening = models.TextField()
    image = models.ImageField(
        upload_to=article_pic_path, blank=True, null=True)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    topics = models.ManyToManyField('Topic')

    def __str__(self):
        return self.title


class Topic(models.Model):
    """Topic model object for filtering articles."""
    name = models.CharField(max_length=255)
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class Comment(models.Model):
    """Comment model object to leave comments on articles."""

    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    article = models.ForeignKey(
        Article, related_name='comments', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    content = models.TextField()

    def __str__(self):
        return self.content


class Like(models.Model):
    """Like model object so user can like articles."""
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    article = models.ForeignKey(
        Article, related_name='likes', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'article')

    def __str__(self):
        return f"{self.user} likes {self.article}"
