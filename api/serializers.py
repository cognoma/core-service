from rest_framework import serializers
from api.models import User, Algorithm

class UserSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(required=False, allow_blank=True, max_length=255)
    email = serializers.CharField(required=False, allow_blank=False, max_length=255)
    last_login = serializers.DateTimeField(format='iso-8601')
    created_at = serializers.DateTimeField(read_only=True, format='iso-8601')
    updated_at = serializers.DateTimeField(read_only=True, format='iso-8601')

    def create(self, validated_data):
        return User.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.email = validated_data.get('email', instance.email)
        instance.last_login = validated_data.get('last_login', instance.default_timeout)
        instance.save()
        return instance
