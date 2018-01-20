from rest_framework import serializers


class SocialSignUpSerializer(serializers.Serializer):
    provider = serializers.CharField(
        required=True, max_length=100, write_only=True)
    access_token = serializers.CharField(
        required=True, max_length=1000, write_only=True)