from django.contrib.auth.hashers import check_password, make_password
from rest_framework_mongoengine import serializers as mongoserializers
from rest_framework import serializers
from rest_framework.authentication import get_authorization_header

from gears.models import Gear
from accounts.models import Token

class GearSerializer(mongoserializers.DocumentSerializer):

    serializers.ReadOnlyField(source='owner.name')
    
    class Meta:
        model = Gear
        fields = '__all__'

    def create(self, validated_data):
        return Gear.objects.create(**validated_data)
