from django.contrib.auth.models import User
from rest_framework import serializers
from .models import Space, Folder, Group, Tag, Project


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username')


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'


class GroupSerializer(serializers.ModelSerializer):
    members = UserSerializer(many=True, read_only=True)

    class Meta:
        model = Group
        fields = '__all__'


class SpaceSerializer(serializers.ModelSerializer):
    # Add nested serializers for related models
    group = GroupSerializer(read_only=True)
    # Assuming a many-to-many relationship
    tags = TagSerializer(many=True, read_only=True)

    class Meta:
        model = Space
        fields = '__all__'  # This will now include the complete objects for 'group' and 'tags'


class FolderSerializer(serializers.ModelSerializer):
    space = SpaceSerializer(read_only=True)

    class Meta:
        model = Folder
        fields = '__all__'


class ProjectSerializer(serializers.ModelSerializer):
    folder = FolderSerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    is_overdue = serializers.SerializerMethodField()
    owner = UserSerializer(read_only=True)

    class Meta:
        model = Project
        fields = '__all__'

    def get_is_overdue(self, obj):
        return obj.is_overdue()