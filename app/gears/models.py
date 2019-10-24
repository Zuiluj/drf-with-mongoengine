from django.db import models
from django_mongoengine import fields, Document
from mongoengine import CASCADE

from accounts.models import User
# Create your models here.

class Gear(Document):
    name = fields.StringField()
    gear_type = fields.StringField()
    price = fields.FloatField()

    owner = fields.ReferenceField(User, reverse_delete_rule=CASCADE)

    USERNAME_FIELD = 'name'
    REQUIRED_FIELDS = ['name', 'gear_type', 'price']

    def __str__(self):
        return self.name

    