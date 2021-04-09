from django.db import models
from django.contrib.auth.models import User

class Note(models.Model):
    title = models.CharField(max_length=200, primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    modify_date = models.DateTimeField('date published', auto_now_add=True)
    doc = models.DateTimeField('date published', auto_now_add=True)
 

    def __str__(self):
        return "Title: {} \nContent: {} \nDate of Creation: {} \nLast modify: {}".format(self.title, self.content, self.doc, self.modify_date) 
