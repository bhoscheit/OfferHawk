from rest_framework import serializers
from realty.models import *

class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = [f.name for f in Transaction._meta.get_fields()]

class PropertySerializer(serializers.ModelSerializer):
    transactions = TransactionSerializer(many=True, read_only=True)

    class Meta:
        model = Property
        fields = [f.name for f in Property._meta.get_fields()]
