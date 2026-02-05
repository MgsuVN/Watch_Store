from django.db import models

class Watch(models.Model):
    name = models.CharField(max_length=255)
    price = models.IntegerField()
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='watches/', blank=True, null=True)
    brand = models.TextField(blank=True)

    def __str__(self):
        return self.name
