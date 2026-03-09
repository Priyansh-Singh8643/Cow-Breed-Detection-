from django.db import models
from django.contrib.auth.models import User

class CowBreed(models.Model):
    breed_name = models.CharField(max_length=100)
    image = models.ImageField(upload_to='cow_breeds/')
    origin = models.CharField(max_length=100)
    milk_production = models.CharField(max_length=100)
    description = models.TextField()

    def __str__(self):
        return self.breed_name

class SearchHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='search_history/')
    predicted_breed = models.CharField(max_length=100)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.predicted_breed} at {self.timestamp.strftime('%Y-%m-%d %H:%M')}"
