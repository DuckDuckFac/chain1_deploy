from django.db import models

# Create your models here.
class Stock(models.Model):
    code = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=50)

    def __str__(self):
        return f'{self.name} ({self.code})'