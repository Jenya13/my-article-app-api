""" 
Serializers for the user API View.
"""

from django.contrib.auth import (get_user_model, authenticate)
from django.utils.translation import gettext as _
from rest_framework import serializers
from django.core.exceptions import ValidationError


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

    class Meta:
        model = get_user_model()
        fields = ['email', 'password', 'first_name',
                  'last_name', 'bio', 'contact_me']
        extra_kwargs = {'password': {'write_only': True, 'min_length': 5}}

    def create(self, validated_data):
        """Create and return user with encypted password."""
        return get_user_model().objects.create_user(**validated_data)

    def update(self, instance, validated_data):
        """Method for updating user info."""
        instance.first_name = validated_data.get(
            'first_name', instance.first_name)
        instance.last_name = validated_data.get(
            'last_name', instance.last_name)
        instance.bio = validated_data.get('bio', instance.bio)
        instance.contact_me = validated_data.get(
            'contact_me', instance.contact_me)
        instance.save()
        return instance

    def validate(self, data):
        """
        This method is called after all field-level validations are passed.
        """
        # Ensure that the first character of the name fields is capitalized
        data['first_name'] = data['first_name'].capitalize()
        data['last_name'] = data['last_name'].capitalize()

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
