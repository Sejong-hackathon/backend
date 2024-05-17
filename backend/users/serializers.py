from rest_framework import serializers


class LoginSerializer(serializers.Serializer):
    id = serializers.CharField(max_length=50)
    pw = serializers.CharField(max_length=50)
