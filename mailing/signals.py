from django.db.models.signals import post_save
from django.dispatch import receiver

from mailing import models
from mailing.datatools.mailing_tasks import process_mailing


@receiver(post_save, sender=models.Mailing)
def create_mailing(
        sender: models.Mailing, instance: models.Mailing,
        created: bool, **kwargs: dict
) -> None:
    if created:
        process_mailing(instance)
