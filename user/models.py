import os
import uuid
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils.translation import gettext as _
from django.utils.text import slugify


class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError("The given email must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self._create_user(email, password, **extra_fields)


class User(AbstractUser):
    username = None
    email = models.EmailField(_("email address"), unique=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []
    objects = UserManager()


def profile_image_file_path(instance, filename) -> str:
    _, ext = os.path.splitext(filename)
    filename = f"{slugify(instance.user.first_name)}-{slugify(instance.user.last_name)}-{uuid.uuid4()}{ext}"

    return os.path.join("uploads", "profile-images", filename)


class Profile(models.Model):
    class Gender(models.TextChoices):
        FEMALE = "female"
        MALE = "male"
        OTHER = "other"

    gender = models.CharField(
        max_length=6,
        choices=Gender.choices
    )
    info = models.TextField()
    image = models.ImageField(null=True, upload_to=profile_image_file_path)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    follows = models.ManyToManyField(
        "self",
        related_name="followed_by",
        symmetrical=False,
        blank=True
    )
    