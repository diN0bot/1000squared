from django import forms
from django.db import models


class CatalystPic(models.Model):
    pic = models.ImageField(upload_to='uploaded_pics/')

class CatalystPicForm(forms.ModelForm):
    class Meta:
        model = CatalystPic
        fields = ['pic']