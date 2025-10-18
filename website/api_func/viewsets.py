from rest_framework import viewsets
from website.api_func import serializers
from website import models

class FuncViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.FuncSerializer
    queryset = models.Funcionario.objects.all()