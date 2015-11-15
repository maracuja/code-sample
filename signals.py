from django.db.models.signals import post_save
from django.dispatch import receiver
from tasks import queue_translation

import logging
opta_logger = logging.getLogger('epl.ingest.opta')

from articles.models import ArticleContent
from promotions.models import HomepageContent


@receiver(post_save, sender=ArticleContent)
def ac_notify_translator(sender, instance, created, **kwargs):
    if instance.status == 3 and instance.translated is False:
        locale = instance.territory.language
        queue_translation.delay('articles_ArticleContent', instance.id, locale)


@receiver(post_save, sender=HomepageContent)
def hpc_notify_translator(sender, instance, created, **kwargs):
    if instance.status == 3 and instance.translated is False:
        locale = instance.territory.language
        queue_translation.delay('promotions_HomepageContent', instance.id, locale)
