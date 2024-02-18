from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from core.user.serializers import UserSerializer
from core.abstract.serializers import AbstractSerializer
from core.post.models import Post
from core.user.models import User


class PostSerializer(AbstractSerializer):
    author = serializers.SlugRelatedField(queryset=User.objects.all(), slug_field="public_id")
    liked = serializers.SerializerMethodField()  # связан с get_liked get_<field_name>
    likes_count = serializers.SerializerMethodField()  # связан get_likes_count get_<field_name>

    def validate_author(self, value):
        if self.context["request"].user != value:
            raise ValidationError("You can't create a post for another user")

        return value

    def update(self, instance, validated_data):
        if not instance.edited:
            validated_data["edited"] = True
        instance = super().update(instance, validated_data)

        return instance

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        author = User.objects.get_object_by_public_id(rep["author"])
        rep["author"] = UserSerializer(author).data
        return rep

    def get_liked(self, instance):
        request = self.context.get("request", None)
        if request is None or request.user.is_anonymous:
            return False

        return request.user.has_liked(instance)

    def get_likes_count(self, instance):
        return instance.liked_by.count()

    class Meta:
        model = Post
        # List of all the fields that can be included in a request or a response
        fields = ["id", "author", "body", "edited", "created", "liked", "likes_count", "updated"]
        read_only_fields = ["edited"]