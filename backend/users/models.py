from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models


class CustomUserManager(BaseUserManager):
    def create_user(self, student_id, password=None, **extra_fields):
        """
        새로운 일반 사용자를 생성
        """
        if not student_id:
            raise ValueError('The Student ID must be set')
        user = self.model(student_id=student_id, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, student_id, password=None, **extra_fields):
        """
        새로운 슈퍼유저를 생성
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(student_id, password, **extra_fields)


class UserProfile(AbstractBaseUser, PermissionsMixin):
    student_id = models.CharField(primary_key=True, max_length=10, unique=True)
    name = models.CharField(max_length=50)
    year = models.IntegerField()
    major = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = CustomUserManager()

    USERNAME_FIELD = 'student_id'

    def __str__(self):
        return self.student_id
