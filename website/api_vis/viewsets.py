from rest_framework import viewsets
from website.api_vis import serializers
from website import models

class VisViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.VisSerializer
    queryset = models.Visitante.objects.all()