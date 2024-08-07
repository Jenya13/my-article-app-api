""" 
Serializers for Article API.
"""
from core.models import Article, Comment, Topic, Like
from rest_framework import serializers
from app.utils.image_processing import process_image


class LikeSerializer(serializers.ModelSerializer):
    """Serializer for likes."""
    # user_id = serializers.CharField(source='user.id', read_only=True)
    user_name = serializers.SerializerMethodField(
        read_only=True)
    article_id = serializers.CharField(source='article.id', read_only=True)

    class Meta:
        model = Like
        fields = ['id', 'user_name', 'article_id', 'created_at']
        read_only_fields = ['id', 'created_at']

    def create(self, validated_data):
        """Method set a like to article, if a user already set like error raised."""
        user = validated_data['user']
        article_id = validated_data['article_id']
        if Like.objects.filter(user=user, article_id=article_id).exists():
            raise serializers.ValidationError(
                {'error': 'You have already liked this article.'})
        return super().create(validated_data)

    def get_user_name(self, obj):
        """Method to get the author name."""
        return f"{obj.user.first_name} {obj.user.last_name}"


class TopicSerializer(serializers.ModelSerializer):
    """Serializer for topics."""

    class Meta:
        model = Topic
        fields = ['id', 'name']
        read_only_fields = ['id']


class CommentSerializer(serializers.ModelSerializer):
    """Serializer for comments"""

    # user_id = serializers.CharField(source='user.id', read_only=True)
    user_name = serializers.SerializerMethodField(
        read_only=True)

    class Meta:
        model = Comment
        fields = ['id', 'user_name', 'content', 'created_at', 'updated_at']
        read_only_fields = ['id',  'created_at', 'updated_at']

    def get_user_name(self, obj):
        """Method to get the author name."""
        return f"{obj.user.first_name} {obj.user.last_name}"


class ArticleSerializer(serializers.ModelSerializer):
    """Serializer for article."""
    author = serializers.SerializerMethodField(
        read_only=True)
    topics = TopicSerializer(many=True, required=False)
    likes_count = serializers.SerializerMethodField()
    image = serializers.ImageField(required=False, allow_null=True)

    class Meta:
        model = Article
        fields = ['id', 'author', 'title', 'image',
                  'created_at', 'updated_at', 'likes_count', 'topics']
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_likes_count(self, obj):
        """Method count likes for article."""
        return obj.likes.count()

    def get_author(self, obj):
        """Method to get the author name."""
        return f"{obj.user.first_name} {obj.user.last_name}"

    def _get_or_create_topics(self, topics, article):
        """Handle getting or creating topics."""
        auth_user = self.context['request'].user
        for topic in topics:
            topic_obj, created = Topic.objects.get_or_create(
                user=auth_user, **topic)
            article.topics.add(topic_obj)

    def create(self, validated_data):
        """Create an article."""

        topics = validated_data.pop('topics', [])
        article = Article.objects.create(**validated_data)
        self._get_or_create_topics(topics, article)
        return article

    def update(self, instance, validated_data):
        """Update Article."""
        image = validated_data.get('image', None)
        if image and instance.image:
            instance.image.delete(save=False)
            processed_image = process_image(image, 'PNG', (700, 400))
            validated_data['image'] = processed_image

        topics = validated_data.pop('topics', None)
        if topics is not None:
            instance.topics.clear()
            self._get_or_create_topics(topics, instance)

        for attr, value in validated_data.items():
            if attr == 'image' and value is None:
                # Skip updating image field if value is None to retain the existing image
                continue
            setattr(instance, attr, value)

        instance.save()
        return instance


class ArticleDetailSerializer(ArticleSerializer):
    """Serializer for detail view."""
    comments = CommentSerializer(many=True, required=False)

    class Meta(ArticleSerializer.Meta):
        fields = ArticleSerializer.Meta.fields + \
            ['opening', 'content', 'comments',]
