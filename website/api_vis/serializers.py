from rest_framework import serializers
from website import models

class VisSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Visitante
        fields = '__all__'