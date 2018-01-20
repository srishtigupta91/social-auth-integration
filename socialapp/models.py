from django.db import models

# Create your models here.
from builtins import ValueError

from django.utils import timezone
from django.utils.http import urlquote
from django.utils.translation import ugettext_lazy as _
from django.core.mail import send_mail
from django.contrib.auth.models import (
    AbstractBaseUser, PermissionsMixin, Group)
from django.contrib.auth.models import BaseUserManager

from phonenumber_field.modelfields import PhoneNumberField


class UserManager(BaseUserManager):

    def _create_user(self, email, password,
                     is_staff, is_superuser, **extra_fields):
        """

        Creates and saves a User with the given email and password.

        """
        now = timezone.now()
        if not email:
            raise ValueError('The given email must be set')
        email = self.normalize_email(email)
        if is_superuser:
            extra_fields['is_active'] = is_superuser
        user = self.model(email=email,
                          is_staff=is_staff,
                          is_superuser=is_superuser, last_login=now,
                          date_joined=now, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        if is_superuser:
            group, create = Group.objects.get_or_create("superadmin")
            user.groups = [group]
            user.save()
        return user

    def create_user(self, email, password=None, **extra_fields):
        return self._create_user(email, password, False, False,
                                 **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        extra_fields['role'] = User.ADMIN
        return self._create_user(email, password, True, True,
                                 **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """
    A fully featured User model with admin-compliant permissions that uses
    a full-length email field as the username.

    Email and password are required. Other fields are optional.
    """
    MALE = '1'
    FEMALE = '2'
    GENDER = (
        (MALE, _("Male")),
        (FEMALE, _("Female"))
    )

    email = models.EmailField(_('Email address'), max_length=254, unique=True)
    name = models.CharField(_('Name'), max_length=30, null=True, blank=True)
    screen_name = models.CharField(max_length=255, null=True, blank=True)
    is_staff = models.BooleanField(_('staff status'), default=False,
                                   help_text=_('Designates whether the user can log into this admin '
                                               'site.'))
    is_active = models.BooleanField(_('active'), default=False,
                                    help_text=_('Designates whether this user should be treated as '
                                                'active. Unselect this instead of deleting accounts.'))
    is_block = models.BooleanField(default=False)
    date_joined = models.DateTimeField(_('date joined'), default=timezone.now)
    dob = models.DateField(null=True, blank=True)
    gender = models.CharField(
        verbose_name=_("select gender."),
        max_length=1,
        choices=GENDER
    )
    image = models.ImageField(
        verbose_name=_("Upload Image."),
        upload_to='profile/',
        null=True,
        blank=True
    )
    last_active = models.DateField(auto_now=True)
    contact_number = PhoneNumberField(blank=True, null=True)
    addressline_1 = models.CharField(max_length=1000, null=True, blank=True)
    addressline_2 = models.CharField(max_length=1000, null=True, blank=True)
    country = models.CharField(max_length=200, null=True, blank=True)
    region = models.CharField(max_length=200, null=True, blank=True)
    city = models.CharField(max_length=250, null=True, blank=True)
    zip_code = models.IntegerField(default=0, null=True, blank=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']

    class Meta:
        verbose_name = _('User')
        verbose_name_plural = _('Users')

    def get_absolute_url(self):
        return "/users/%s/" % urlquote(self.email)

    def __str__(self):
        return self.email

    @property
    def age(self):
        current_time = timezone.now()
        if self.dob:
            age = current_time.year - self.dob.year
            return age

    def get_full_name(self):
        """
        Returns the first_name plus the last_name, with a space in between.
        """
        return self.name

    def get_short_name(self):
        "Returns the short name for the user."
        return self.name

    def email_user(self, subject, message, from_email=None):
        """
        Sends an email to this User.
        """
        send_mail(subject, message, from_email, [self.email])