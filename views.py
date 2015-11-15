# -*- coding: utf-8 -*-

from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status

from services.Smartling import SmartlingService
from utils import WhackyJSONRenderer


class Receive(generics.ListAPIView):
    renderer_classes = (WhackyJSONRenderer,)

    def list(self, request, *args, **kwargs):
        ss = SmartlingService(request.GET['locale'])
        response = ss.get_from_translator(request)
        return Response(response, status=status.HTTP_201_CREATED, content_type='text/html; charset=utf-8')
