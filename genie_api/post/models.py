from django.db.models import CharField, DateField, DateTimeField, ForeignKey, IntegerField, TextField, ManyToManyField
from django.db import models

from genie_api.appuser.models import User

# Create your models here.

class Post(models.Model):

    class Meta:
        db_table = 'post'
        ordering = ('created',)

    id = IntegerField(primary_key=True, unique=True, auto_created=True)
    created = DateTimeField(auto_now=True)
    content = TextField(blank=True)
    reply_number = IntegerField(default=0)
    created_by = ForeignKey(User)

    def get_as_data(self):
        return {"id": self.id,
                "created": str(self.created),
                "content": self.content,
                "reply_number": self.reply_number,#}
                "created_by": self.created_by.get_as_data()}
