from django.contrib.auth.models import (AbstractBaseUser, BaseUserManager,
                                        PermissionsMixin)
from django.core.validators import validate_email
from django.db import models
from rest_framework import serializers
from spaces.models import Folder

# Create your models here.


class UserProfileManager(BaseUserManager):
    """Manager for user profiles"""

    def create_user(self, email, name, password=None):
        """Create a new user profile"""
        if not email:
            raise ValueError("User must have an email address")
        validate_email(email)
        email = self.normalize_email(email)
        user = self.model(email=email, name=name)
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, email, name, password):
        """Create a new superuser profile"""
        user = self.create_user(email, name, password)
        user.is_admin = True
        user.is_superuser = True
        user.save(using=self._db)

        return user


class UserProfile(AbstractBaseUser, PermissionsMixin):
    """Database model for users in the system"""

    email = models.EmailField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    is_admin = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    objects = UserProfileManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["name"]

    @property
    def is_staff(self):
        return self.is_admin

    def __str__(self):
        """Return string representation of our user"""
        return self.email


class Tag(models.Model):
    name = models.CharField(max_length=100, unique=True)


class Chat(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length=1000, blank=True, default="")
    tags = models.ManyToManyField(Tag, related_name="chats", blank=True)
    prompt = models.CharField(max_length=4000)
    author = models.ForeignKey(
        "api.UserProfile", related_name="chats", on_delete=models.CASCADE
    )
    folder = models.ForeignKey(
        Folder, related_name="chats", on_delete=models.SET_NULL, null=True, blank=True
    )

    response = models.TextField()
    created_at = models.DateField(auto_now=True)

    class Meta:
        ordering = ["created_at"]
