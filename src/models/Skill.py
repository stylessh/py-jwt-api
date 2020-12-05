import datetime
from mongoengine import Document, StringField, DateTimeField


class Skill(Document):
    name = StringField(required=True)
    created_at = DateTimeField(required=True, default=datetime.datetime.now())
