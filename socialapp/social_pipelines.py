import hashlib
from rest_framework import exceptions

from .models import User
from .exceptions import SocialAuthEmailNotExists
USER_FIELDS = ['username', 'email']


def auto_logout(*args, **kwargs):
    """Do not compare current user with new one"""
    return {'user': None}


def create_user(strategy, details, backend, user=None, *args, **kwargs):
    if user:
        return {'is_new': False}
    fields = dict((name, kwargs.get(name, details.get(name)))
                  for name in backend.setting('USER_FIELDS', USER_FIELDS))
    fields['name'] = details.get('username')
    fields['is_active'] = True
    fields['role'] = User.USER
    response = kwargs.get('response', {})
    fields['gender'] = User.MALE if response.get(
        'gender') == "male" else User.FEMALE
    print(fields)
    if not fields:
        return

    return {
        'is_new': True,
        'user': strategy.create_user(**fields)
    }


def save_avatar(strategy, details, user=None, *args, **kwargs):
    """Get user avatar from social provider."""
    if user:
        backend_name = kwargs['backend'].__class__.__name__.lower()
        response = kwargs.get('response', {})
        social_thumb = None
        if 'facebook' in backend_name:
            if 'id' in response:
                social_thumb = (
                    'http://graph.facebook.com/{0}/picture?type=normal'
                ).format(response['id'])
        elif 'twitter' in backend_name and response.get('profile_image_url'):
            social_thumb = response['profile_image_url']
        elif 'googleoauth2' in backend_name and response.get('image', {}).get('url'):
            social_thumb = response['image']['url'].split('?')[0]
        else:
            social_thumb = 'http://www.gravatar.com/avatar/'
            social_thumb += hashlib.md5(
                user.email.lower().encode('utf8')).hexdigest()
            social_thumb += '?size=100'
        # if social_thumb and user.image != social_thumb:
            # user.image = social_thumb
            # strategy.storage.user.changed(user)


def check_for_email(backend, uid, user=None, *args, **kwargs):
    if not kwargs['details'].get('email'):
        raise SocialAuthEmailNotExists("error in getting email")
