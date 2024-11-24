from rest_framework import status
from rest_framework.response import Response
from rest_framework.settings import api_settings


class OptionMixin:

    def get(self, request, *args, **kwargs):
        serializer = self.get_serializer(self.get_queryset(), many=True)
        return Response(serializer.data)


