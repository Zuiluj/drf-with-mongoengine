from django.contrib.auth import authenticate
from django.contrib.auth.hashers import check_password, make_password
from rest_framework_mongoengine import serializers as mongoserializers
from rest_framework import serializers

from accounts.models import User
from gears.models import Gear


class UserSerializer(mongoserializers.DocumentSerializer): 

    class Meta:
        model = User
        fields = '__all__' # map all fields in User model
        extra_kwargs = {'password': {'write_only': True}} # make password writable but not readable
        
    def create(self, validated_data):
        # hash the password before storing to mongodb
        validated_data['password'] = make_password(validated_data['password'])
        return User.objects.create(**validated_data)


    def update(self, instance, validated_data):
        """ Update the current instance with the provided data"""
        instance.name = validated_data.get('name', instance.name)
        instance.username = validated_data.get('username', instance.username)
        instance.email = validated_data.get('email', instance.email)
        instance.password = make_password(validated_data.get('password', instance.password))
        instance.save()

        return instance


class AuthTokenSerializer(serializers.Serializer):

    username = serializers.CharField()
    password = serializers.CharField()
    
    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')

        if username and password:
            user = User.objects.get(username=username)

            if not user.check_password(password):
                msg = 'Wrong password'
                raise serializers.ValidationError(msg)

            if user:
                if not user.is_active:
                    msg = 'User account is disabled.'
                    raise serializers.ValidationError(msg)
            
            else:
                msg = 'Unable to login with the provided credentials.'
                raise serializers.ValidationError(msg)
            


        else:
            msg = 'Must include username and password'
            raise serializers.ValidationError(msg)

        attrs['user'] = user
        return attrs