from rest_framework import viewsets
from website.api_ter import serializers
from website import models

class TerViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.TerSerializer
    queryset = models.Terceiro.objects.all()