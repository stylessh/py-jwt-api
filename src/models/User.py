import datetime
from mongoengine import Document, StringField, EmailField, DateTimeField, ListField


class User(Document):
    full_name = StringField(required=True)
    username = StringField(required=True, min_length=4)
    email = EmailField(required=True)
    password = StringField(required=True, min_length=8)
    country = StringField(required=True)
    skills = ListField(StringField())
    created_at = DateTimeField(required=True, default=datetime.datetime.now())
