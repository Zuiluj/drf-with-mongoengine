import binascii
import os
import logging

from django.conf import settings
from django.utils import timezone
from django.contrib.auth.hashers import check_password, make_password
from mongoengine import CASCADE
from django_mongoengine import Document, fields

class User(Document):
    name = fields.StringField()
    username = fields.StringField(unique=True)
    email = fields.EmailField(unique=True)

    # these 2 fields are NOT TO BE FILLED
    ratings = fields.IntField(default=0) 
    date_joined = fields.DateTimeField(default=timezone.now, editable=False)

    gears = fields.ListField(
        fields.ReferenceField('Gear'),
        default=[],
        blank=True
        )
    password = fields.StringField(min_length=8, max_length=128)

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['name', 'email', 'password'] 


    def __str__(self):
        return self.username
    
    def get_username(self):
        return self.username

    def get_name(self):
        return self.name

    def get_ratings(self):
        return self.ratings
        
    def is_active(self):
        return True

    def check_password(self, raw_password):
        """ Checks the password if it matches the stored password """
        return check_password(raw_password, self.password)


class Token(Document):
    key = fields.StringField()
    user = fields.ReferenceField(User, on_delete=CASCADE)
    created = fields.DateTimeField(default=timezone.now, editable=False)

    REQUIRED_FIELDS = ['key']

    def save(self, *args, **kwargs):
        if not self.key:
            self.key = self.generate_key()
        return super(Token, self).save(*args, **kwargs)

    def generate_key(self):
        return binascii.hexlify(os.urandom(20)).decode()

    def __str__(self):
        return self.key