from rest_framework import serializers
from website import models


class FuncSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Funcionario
        fields = '__all__'
