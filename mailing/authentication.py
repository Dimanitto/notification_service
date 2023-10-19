from django.contrib.auth import models
from social_core.backends.google import GoogleOAuth2


def make_user_staff(
        backend: GoogleOAuth2, user: models.User, *args, **kwargs
) -> None:
    """
    Добавить возможность просматривать админку новым
    авторизованным пользователям через google account
    """
    group, _ = models.Group.objects.get_or_create(name='Google_authorization')
    user.is_staff = True
    user.groups.add(group)
    user.save(update_fields=['is_staff'])
