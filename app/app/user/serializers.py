""" 
Serializers for the user API View.
"""

from django.contrib.auth import (get_user_model, authenticate)
from django.utils.translation import gettext as _
from rest_framework import serializers
from django.core.exceptions import ValidationError
from app.utils.image_processing import process_image


def validate_name(value):
    """
    Validator function to check if the name contains only letters from a-z or A-Z,
    and convert the first character to uppercase.
    """
    if not value.isalpha():
        raise ValidationError("Name must contain only letters.")
    return value.capitalize()


class UserSerializer(serializers.ModelSerializer):
    """Serializer for user object."""
    first_name = serializers.CharField(validators=[validate_name])
    last_name = serializers.CharField(validators=[validate_name])
    image = serializers.ImageField(required=False, allow_null=True)

    class Meta:
        model = get_user_model()
        fields = ['email', 'password', 'image', 'first_name',
                  'last_name', 'bio', 'contact_me']
        extra_kwargs = {'password': {'write_only': True, 'min_length': 5}}

    def create(self, validated_data):
        """Create and return user with encypted password."""
        image = validated_data.pop('image', None)
        if image:
            processed_image = process_image(image)
            validated_data['image'] = processed_image
        return get_user_model().objects.create_user(**validated_data)

    def update(self, instance, validated_data):
        """Method for updating user info."""
        image = validated_data.get('image', None)
        if image and instance.image:
            instance.image.delete(save=False)
            processed_image = process_image(image)
            validated_data['image'] = processed_image

        for attr, value in validated_data.items():
            if attr == 'password':
                instance.set_password(value)
            else:
                setattr(instance, attr, value)
        instance.save()
        return instance

    def validate(self, data):
        """
        This method is called after all field-level validations are passed.
        """
        if 'first_name' in data:
            data['first_name'] = validate_name(data['first_name'])
        if 'last_name' in data:
            data['last_name'] = validate_name(data['last_name'])
        return data


class AuthTokenSerializer(serializers.Serializer):
    """Serializer for the user auth token."""
    email = serializers.EmailField()
    password = serializers.CharField(
        style={'input_type': 'password'}, trim_whitespace=False,)

    def validate(self, attrs):

        email = attrs.get('email')
        password = attrs.get('password')
        user = authenticate(
            request=self.context.get('request'),
            username=email,
            password=password,
        )

        if not user:
            msg = _('Unable to authenticate with provided credentials.')
            raise serializers.ValidationError(msg, code='authorization')

        attrs['user'] = user
        return attrs

    def update(self, instance, validated_data):
        """Update and return user."""

        password = validated_data.pop('password', None)
        user = super().update(instance, validated_data)
        if password:
            user.set_password(password)
            user.save()
        return user
