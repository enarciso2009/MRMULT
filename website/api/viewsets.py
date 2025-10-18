from rest_framework import viewsets
from website.api import serializers
from website import models

class EventoViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.EventoSerializer
    queryset = models.Evento.objects.all()



