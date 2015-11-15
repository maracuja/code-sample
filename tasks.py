# -*- coding: utf-8 -*-

import logging

from celery import shared_task
from services.Smartling import SmartlingService


opta_logger = logging.getLogger('epl.ingest.opta')


@shared_task
def queue_translation(item_type, item_id, locale):
    opta_logger.info('send_to_translator called: %s id-%s for locale: %s' % (item_type, item_id, locale,))
    ss = SmartlingService(locale)
    ss.post_to_translator(item_type, item_id)
