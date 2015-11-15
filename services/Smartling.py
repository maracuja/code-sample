# -*- coding: utf-8 -*-

import logging
opta_logger = logging.getLogger('epl.ingest.opta')

# from django.db.models.loading import get_model
from django.apps import apps
import json
import os
from eplasia import settings

from translations.libs.smartlingApiSdk.SmartlingFileApi import SmartlingFileApiFactory
from translations.libs.smartlingApiSdk.UploadData import UploadData

from BaseService import BaseService


SMARTLING_SETTINGS = {
    'file_type': 'JSON',
    'file_path': '/tmp/',
    'sandbox_mode': True,
    'locales': {
        'ja-jp': {
            'api_key': 'sdflskjdfsldkfj',
            'project_id': 'sdfsdfsdf',
        },
        'in-id': {
            'api_key': 'sdflskjdfsldkfj',
            'project_id': 'sdfsdfsdf',
        },
        'id-id': {
            'api_key': 'sdflskjdfsldkfj',
            'project_id': 'sdfsdfsdf',
        },
        'vi-vn': {
            'api_key': 'sdflskjdfsldkfj',
            'project_id': 'sdfsdfsdf',
        }
    }
}


class SmartlingService(BaseService):
    def __init__(self, locale):
        self.LOCALE = locale.lower()
        if settings.ENV == 'prod':
            self.ENV = 'translate'
        else:
            self.ENV = settings.ENV

        if self.LOCALE in SMARTLING_SETTINGS['locales']:
            self.FILE_PATH = SMARTLING_SETTINGS['file_path']
            self.FILE_TYPE = SMARTLING_SETTINGS['file_type']
            self.CALLBACK_URL = settings.SMARTLING_CALLBACK
            self.MY_API_KEY = SMARTLING_SETTINGS['locales'][self.LOCALE]['api_key']
            self.MY_PROJECT_ID = SMARTLING_SETTINGS['locales'][self.LOCALE]['project_id']
            self.SANDBOX_MODE = SMARTLING_SETTINGS['sandbox_mode']
        else:
            opta_logger.info('locale %s is not supported', self.LOCALE)

    def serialise(self, item_type, item_id):
        """
        Turn the django model into a JSON object that can be sent to Smartling.
        ie a list of strings that need translating
        """
        app, model = item_type.split('_')
        item = apps.get_model(app, model).objects.get(pk=item_id)
        doc = {}

        for field in item.SMARTLING_FIELDS['fields']:
            doc[field] = {
                "translation": item.__dict__[field],
            }

        if 'subobjects' in item.SMARTLING_FIELDS:
            for subobject in item.SMARTLING_FIELDS['subobjects']:
                subs = getattr(item, subobject).all()
                for sub in subs:
                    for field in sub.SMARTLING_FIELDS['fields']:
                        field_name = "%s_%s_%s" % (subobject, sub.id, field,)
                        doc[field_name] = {
                            "translation": sub.__dict__[field],
                        }

        file_name = "%s.%s.%s.json" % (self.ENV, item_type, item_id,)
        with open('%s%s' % (self.FILE_PATH, file_name,), 'w') as outfile:
            json.dump(doc, outfile)
        return file_name

    def delete_upload(self, file_name):
        os.remove(file_name)

    def deserialise(self, item_type, item_id, data):
        """
        Turn the list of translations back into a django model object
        """
        app, model = item_type.split('_')
        item = apps.get_model(app, model).objects.get(pk=item_id)
        opta_logger.info("Deserialising the object %s", item.id)
        opta_logger.info("Here is the data %s", data)
        data_dict = json.loads(data, encoding='utf-8')
        for field in item.SMARTLING_FIELDS['fields']:
            item.__dict__[field] = data_dict[field]['translation']

        if 'subobjects' in item.SMARTLING_FIELDS:
            for subobject in item.SMARTLING_FIELDS['subobjects']:
                subobject_json = {}
                for field in data_dict:
                    if subobject in field:
                        sub_object, sub_id, sub_field = field.split('_')
                        if sub_id in subobject_json:
                            subobject_json[sub_id].update({sub_field: data_dict[field]['translation']})
                        else:
                            subobject_json.update({sub_id: {sub_field: data_dict[field]['translation']}})

                for obj in subobject_json:
                    sub_item = getattr(item, subobject).get(pk=obj)
                    for field in subobject_json[obj]:
                        sub_item.__dict__[field] = subobject_json[obj][field]
                    opta_logger.info("Saving subobject: %s", sub_item.id)
                    sub_item.save()

        return item

    def post_to_translator(self, item_type, item_id):
        """
        Send the django model to Smartling.
        """
        if self.LOCALE in SMARTLING_SETTINGS['locales']:
            opta_logger.info('post_to_translator called: %s', item_id)

            FILE_NAME = self.serialise(item_type, item_id)
            uploadDataUtf16 = UploadData(self.FILE_PATH, FILE_NAME, self.FILE_TYPE)
            uploadDataUtf16.setApproveContent("true")
            uploadDataUtf16.setCallbackUrl(self.CALLBACK_URL)
            opta_logger.info('temp file is here: %s %s' % (self.FILE_PATH, FILE_NAME,))

            fapi = SmartlingFileApiFactory().getSmartlingTranslationApi(self.SANDBOX_MODE, self.MY_API_KEY, self.MY_PROJECT_ID)
            response = fapi.upload(uploadDataUtf16)
            if response:
                opta_logger.info('file posted: %s', FILE_NAME)
                opta_logger.info(response)
                self.delete_upload('%s%s' % (self.FILE_PATH, FILE_NAME,))
            else:
                opta_logger.info('file not posted: sadface.gif')
            return True
        else:
            opta_logger.info('locale %s is not supported', self.LOCALE)

    def get_from_translator(self, request):
        """
        Get the translations from Smartling and save them to the database into
        the model instance that they were sent from.
        """
        if self.LOCALE in SMARTLING_SETTINGS['locales']:
            FILE_NAME = request.GET['fileUri']
            environment_name, item_type, item_id, file_type = FILE_NAME.split('.')

            uploadDataUtf16 = UploadData(self.FILE_PATH, FILE_NAME, self.FILE_TYPE)
            uploadDataUtf16.setApproveContent("true")

            fapi = SmartlingFileApiFactory().getSmartlingTranslationApi(self.SANDBOX_MODE, self.MY_API_KEY, self.MY_PROJECT_ID)
            sl_response, sl_status = fapi.get(uploadDataUtf16.name, self.LOCALE)
            incoming_object = self.deserialise(item_type, item_id, sl_response)
            return incoming_object.save_translation()
        else:
            opta_logger.info('locale %s is not supported', self.LOCALE)
