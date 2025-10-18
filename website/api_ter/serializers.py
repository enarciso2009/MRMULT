from rest_framework import serializers
from website import models

class TerSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Terceiro
        fields = '__all__'
