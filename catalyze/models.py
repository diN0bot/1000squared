from django import forms
from django.db import models
import os
import settings


class CatalystPic(models.Model):
    upload_to = os.path.join(settings.BASE_DIR, 'uploaded_pics/')
    pic = models.ImageField(upload_to=upload_to)

class CatalystPicForm(forms.ModelForm):
    class Meta:
        model = CatalystPic
        fields = ['pic']